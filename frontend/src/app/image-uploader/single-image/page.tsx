'use client';

import { SingleImageUploader } from '@/components';
import { useDefaultStore } from '@/stores';

export default function ImageUploaderPage() {
  const { uploadedImage, setUploadedImage, removeUploadedImage } =
    useDefaultStore();

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-8 text-center">
          Image Uploader
        </h1>
        <SingleImageUploader
          image={uploadedImage}
          onImageUpload={setUploadedImage}
          onImageRemove={removeUploadedImage}
        />
      </div>
    </div>
  );
}
