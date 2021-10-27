/*
 * Copyright (c) 2008-2017, NVIDIA CORPORATION.  All rights reserved.
 *
 * NVIDIA CORPORATION and its licensors retain all intellectual property
 * and proprietary rights in and to this software, related documentation
 * and any modifications thereto.  Any use, reproduction, disclosure or
 * distribution of this software and related documentation without an express
 * license agreement from NVIDIA CORPORATION is strictly prohibited.
 */


#include "RTdef.h"
#if RT_COMPILE
#ifndef RT_RENDERABLE_H
#define RT_RENDERABLE_H

#include "PsArray.h"
#include "PsUserAllocated.h"
#include "PxVec2.h"

namespace nvidia
{
namespace apex
{
	class UserRenderer;
	class UserRenderVertexBuffer;
	class UserRenderIndexBuffer;
	class UserRenderBoneBuffer;
	class UserRenderResource;
}
using namespace shdfnd;

namespace fracture
{

class Actor;
class Convex;

class Renderable : public UserAllocated
{
public:
	Renderable();
	~Renderable();

	// Called by rendering thread
	void updateRenderResources(bool rewriteBuffers, void* userRenderData);
	void dispatchRenderResources(UserRenderer& api);

	// Per tick bone update, unless Actor is dirty
	void updateRenderCache(Actor* actor);

	// Returns the bounds of all of the convexes
	PxBounds3	getBounds() const;

private:
	// Called by actor after a patternFracture (On Game Thread)
	void updateRenderCacheFull(Actor* actor);

	// To Handle Multiple Materials
	struct SubMesh
	{
		SubMesh(): renderResource(NULL) {}

		physx::shdfnd::Array<uint32_t>			mIndexCache;
		UserRenderResource*	renderResource;
	};
	// To Handle Bone Limit
	struct ConvexGroup
	{
		physx::shdfnd::Array<SubMesh>			mSubMeshes;
		physx::shdfnd::Array<Convex*>			mConvexCache;
		physx::shdfnd::Array<PxVec3>			mVertexCache;
		physx::shdfnd::Array<PxVec3>			mNormalCache;
		physx::shdfnd::Array<PxVec2>			mTexcoordCache;
		physx::shdfnd::Array<uint16_t>			mBoneIndexCache;
		physx::shdfnd::Array<PxMat44>			mBoneCache;
	};
	// Shared by SubMeshes
	struct MaterialInfo
	{
		MaterialInfo(): mMaxBones(0), mMaterialID(0) {}

		uint32_t		mMaxBones;
		ResID		mMaterialID;
	};
	//
	physx::shdfnd::Array<ConvexGroup>	mConvexGroups;
	physx::shdfnd::Array<MaterialInfo> mMaterialInfo;

	UserRenderVertexBuffer*	mVertexBuffer;
	UserRenderIndexBuffer*	mIndexBuffer;
	UserRenderBoneBuffer*		mBoneBuffer;
	uint32_t						mVertexBufferSize;
	uint32_t						mIndexBufferSize;
	uint32_t						mBoneBufferSize;
	uint32_t						mVertexBufferSizeLast;
	uint32_t						mIndexBufferSizeLast;
	uint32_t						mBoneBufferSizeLast;
	bool						mFullBufferDirty;
	bool valid;
};

}
}

#endif
#endif