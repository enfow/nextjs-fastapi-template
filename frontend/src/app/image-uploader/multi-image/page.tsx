'use client';

import { useState } from 'react';

import { MultiImageUploader } from '@/components';
import { useDefaultStore } from '@/stores';
import { type UploadedImage, useApiStore } from '@/stores/apiStore';

export default function MultiImageUploaderPage() {
  const {
    uploadedImages,
    addMultipleImages,
    removeUploadedImageAt,
    clearAllImages,
  } = useDefaultStore();

  const [minioUploadedImages, setMinioUploadedImages] = useState<
    UploadedImage[]
  >([]);

  const handleMinioUpload = (uploadedImgs: UploadedImage[]) => {
    setMinioUploadedImages((prev) => [...prev, ...uploadedImgs]);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-8 text-center">
          Multi-Image Gallery Uploader
        </h1>
        <p className="text-center text-foreground/60 mb-8 max-w-2xl mx-auto">
          Upload multiple images at once and manage your gallery. Drag and drop
          or click to select multiple files, then upload them to MinIO storage.
        </p>

        <MultiImageUploader
          images={uploadedImages}
          onImagesAdd={addMultipleImages}
          onImageRemove={removeUploadedImageAt}
          onClearAll={clearAllImages}
          maxImages={15}
          directoryName="multi-uploads"
          description="Multi-image gallery upload"
          onMinioUpload={handleMinioUpload}
        />

        {/* MinIO Uploaded Images Display */}
        {minioUploadedImages.length > 0 && (
          <div className="mt-12 p-6 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <h2 className="text-xl font-semibold text-green-800 dark:text-green-300 mb-4">
              ✅ Uploaded to MinIO Storage ({minioUploadedImages.length} images)
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {minioUploadedImages.map((img, index) => (
                <div
                  key={img.id}
                  className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm"
                >
                  <div className="aspect-video bg-gray-100 dark:bg-gray-700 rounded-lg mb-3 overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={img.url}
                      alt={img.original_name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                    <p
                      className="font-medium text-gray-900 dark:text-gray-100 truncate"
                      title={img.original_name}
                    >
                      {img.original_name}
                    </p>
                    <p>Size: {formatFileSize(img.file_size)}</p>
                    {img.image_info && (
                      <p>
                        Dimensions: {img.image_info.width} ×{' '}
                        {img.image_info.height}
                      </p>
                    )}
                    <div className="pt-2">
                      <a
                        href={img.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline text-xs"
                      >
                        View in MinIO →
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t border-green-200 dark:border-green-800">
              <button
                onClick={() => setMinioUploadedImages([])}
                className="text-green-700 dark:text-green-400 hover:text-green-900 dark:hover:text-green-200 text-sm"
              >
                Clear MinIO Gallery
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
