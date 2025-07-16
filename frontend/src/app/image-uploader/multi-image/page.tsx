'use client';

import { MultiImageUploader } from '@/components';
import { useDefaultStore } from '@/stores';

export default function MultiImageUploaderPage() {
  const {
    uploadedImages,
    addMultipleImages,
    removeUploadedImageAt,
    clearAllImages,
  } = useDefaultStore();

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-8 text-center">
          Multi-Image Gallery Uploader
        </h1>
        <p className="text-center text-foreground/60 mb-8 max-w-2xl mx-auto">
          Upload multiple images at once and manage your gallery. Drag and drop
          or click to select multiple files.
        </p>

        <MultiImageUploader
          images={uploadedImages}
          onImagesAdd={addMultipleImages}
          onImageRemove={removeUploadedImageAt}
          onClearAll={clearAllImages}
          maxImages={15}
        />
      </div>
    </div>
  );
}
