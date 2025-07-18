'use client';

import { useState } from 'react';

import { SingleImageUploader } from '@/components';
import { useDefaultStore } from '@/stores';
import { type UploadedImage, useApiStore } from '@/stores/apiStore';

export default function ImageUploaderPage() {
  const { uploadedImage, setUploadedImage, removeUploadedImage } =
    useDefaultStore();

  const { uploadedImages } = useApiStore();
  const [minioUploadedImage, setMinioUploadedImage] =
    useState<UploadedImage | null>(null);

  const handleMinioUpload = (uploadedImg: UploadedImage) => {
    setMinioUploadedImage(uploadedImg);
  };

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-8 text-center">
          Single Image Uploader
        </h1>
        <p className="text-center text-foreground/60 mb-8">
          Upload a single image locally for preview, then upload it to MinIO
          storage.
        </p>

        <SingleImageUploader
          image={uploadedImage}
          onImageUpload={setUploadedImage}
          onImageRemove={removeUploadedImage}
          directoryName="single-uploads"
          description="Single image upload"
          onMinioUpload={handleMinioUpload}
        />

        {/* MinIO Uploaded Image Display */}
        {minioUploadedImage && (
          <div className="mt-8 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <h2 className="text-lg font-semibold text-green-800 dark:text-green-300 mb-2">
              ✅ Uploaded to MinIO Storage
            </h2>
            <div className="space-y-2 text-sm text-green-700 dark:text-green-400">
              <p>
                <strong>File:</strong> {minioUploadedImage.original_name}
              </p>
              <p>
                <strong>Size:</strong>{' '}
                {(minioUploadedImage.file_size / 1024).toFixed(1)} KB
              </p>
              <p>
                <strong>Directory:</strong> {minioUploadedImage.directory_name}
              </p>
              {minioUploadedImage.image_info && (
                <p>
                  <strong>Dimensions:</strong>{' '}
                  {minioUploadedImage.image_info.width} ×{' '}
                  {minioUploadedImage.image_info.height}
                </p>
              )}
              <div className="mt-2">
                <a
                  href={minioUploadedImage.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
                >
                  View in MinIO →
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
