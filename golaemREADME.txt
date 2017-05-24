The git version of PhysX can't be used as is and needs some polyshing.

1.\ Run the physX_to_glm python script, it will:
	- change build options to /MD (profile) and /MDd (debug) in all vcroj files
	- prefix PhysX runtime libraries (.dlls) by glm_ to avoid collision with the DCC plugin
	- postfix Apex  runtime libraries (.dlls) by _glm to avoid collision with the DCC plugin (Apex needs to be postfixed to be able to work with physX, and when used in a project, the post fix needs to be set correctly in the NxApexSDKDesc: apexSDKDesc.dllNamePostfix = "_glm";)
	- fix some missing namespace in few headers (would collide in glm projects otherwise)
	- add some extra accessors that are needed for Apex in Golaem (get physical/graphical mesh vertex/index count)
    - (The python script used to change physx namespace into glm_physx to avoid collisions with PhysX DCC plugin libraries but it's not needed anymore and will forbid the use of GPU acceleration if done)

2.\ To use the GPU acceleration PhysX3Gpu libraries (DEBUG, PROFILE) has to be renamed into glm_PhysX3Gpu to avoid collisions with the PhysX DCC plugin in Maya.
Now you can't expect to simply rename DLL, the corresponding .lib has to target the correct DLL name, so they are to be rebuilt (not simply renamed).
Here is how to do it: (sources: https://support.microsoft.com/fr-fr/help/131313/how-to-create-32-bit-import-libraries-without-.objs-or-source and http://stackoverflow.com/questions/280485/how-do-i-rename-a-dll-but-still-allow-the-exe-to-find-it)

In short:
	- rename PhysX3GpuDEBUG_x64.dll into glm_PhysX3GpuDEBUG_x64.dll
	- run a developer command prompt for visual, and run "dumpbin /EXPORTS glm_PhysX3GpuDEBUG_x64.dll"
	This will display the list of all symbols exposed by the .dll:
	   ordinal hint RVA      name

          1    0 00002FB8 PxCreateCudaContextManager
          2    1 000024FF PxCreatePhysXGpu
          3    2 00004DC2 PxGetSuggestedCudaDeviceOrdinal
          4    3 0000513C PxSetPhysXGpuDelayLoadHook
		  
	The ordinal and name are the 2 values that will be needed to write the glm_PhysX3GpuDEBUG_x64.def file that will be needed to build the .lib file (you can also get these values thanks to dependancy walker).
	
	Now create a glm_PhysX3GpuDEBUG_x64.def file and fill it with the library name and export symbols:
	
	LIBRARY   glm_PhysX3GpuDEBUG_x64  
	EXPORTS  
	   PxCreateCudaContextManager   @1  
	   PxCreatePhysXGpu   @2  
	   PxGetSuggestedCudaDeviceOrdinal   @3  
	   PxSetPhysXGpuDelayLoadHook   @4  
	   
	In the developer command prompt for visual again, run the LIB command that will build the corresponding lib: 
	LIB /MACHINE:x64 /def:glm_PhysX3GpuDEBUG_x64.def
	
	And that's it.
	Use the glm_PhysX3GpuDEBUG_x64.lib that was created instead of the original PhysX3GpuDEBUG_x64.lib to link your project
	Do the same for the PhysX3GpuPROFILE_x64 libraries.
	
3.\ In PxPhysXGpuModuleLoader.cpp file in PhysX project, configure the new gpu library name, and rebuild the PhysX project:
	static const char*	gPhysXGpuLibraryName = "glm_PhysX3Gpu" CONFIG_SUB_STR "_" PLATFORM_SUB_STR ".dll";
	
4.\ To be able to build on Linux:
	The ClothingCollisionType enum in ClothingCollision.h has to be changed: Convex needs to be renamed (there seems to be a define of Convex in our linux dependencies). Let's name it Convex_
	Some PX_PS4 are misused and needs to be fixed: UserRenderInstanceBufferDesc.h UserRenderIndexBufferDesc.h UserRenderSpriteBufferDesc.h ApexSharedUtils.h

	