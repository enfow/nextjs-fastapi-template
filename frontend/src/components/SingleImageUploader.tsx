'use client';

import { useRef, useState } from 'react';

import { type UploadedImage, useApiStore } from '@/stores/apiStore';

import { ImageViewModal } from './ImageViewModal';

interface SingleImageUploaderProps {
  image: string | null;
  onImageUpload: (image: string | null) => void;
  onImageRemove: () => void;
  directoryName?: string;
  description?: string;
  onMinioUpload?: (uploadedImage: UploadedImage) => void;
}

export function SingleImageUploader({
  image,
  onImageUpload,
  onImageRemove,
  directoryName = 'single-uploads',
  description,
  onMinioUpload,
}: SingleImageUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { uploadSingleImage, uploadStatus, resetUploadStatus } = useApiStore();

  const handleFileSelect = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      setCurrentFile(file);
      resetUploadStatus();
      const reader = new FileReader();
      reader.onload = (e) => {
        onImageUpload(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemove = () => {
    onImageRemove();
    setCurrentFile(null);
    resetUploadStatus();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUploadToMinio = async () => {
    if (!currentFile) return;

    const result = await uploadSingleImage(
      currentFile,
      directoryName,
      description
    );
    if (result && onMinioUpload) {
      onMinioUpload(result);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200 min-h-[300px] flex flex-col items-center justify-center
          ${
            isDragOver
              ? 'border-primary bg-primary/5'
              : 'border-foreground/30 hover:border-primary hover:bg-primary/5'
          }
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileInputChange}
          className="hidden"
        />

        {image ? (
          <div className="w-full h-full relative">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={image}
              alt="Uploaded"
              className="max-w-full max-h-64 object-contain mx-auto rounded cursor-pointer hover:opacity-90 transition-opacity"
              onClick={(e) => {
                e.stopPropagation();
                setIsModalOpen(true);
              }}
            />
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleRemove();
              }}
              className="absolute top-2 right-2 bg-black/50 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-black/70 transition-colors"
            >
              ✕
            </button>
          </div>
        ) : (
          <div className="text-center">
            <div className="mb-4">
              <svg
                className="mx-auto h-12 w-12 text-foreground/40"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            <p className="text-lg font-medium text-foreground mb-2">
              Click to upload an image
            </p>
            <p className="text-sm text-foreground/60">
              or drag and drop an image here
            </p>
            <p className="text-xs text-foreground/40 mt-2">
              PNG, JPG, GIF up to 10MB
            </p>
          </div>
        )}
      </div>

      {image && (
        <div className="mt-4 space-y-3">
          {/* Upload to MinIO Button */}
          {currentFile && !uploadStatus.success && (
            <div className="text-center">
              <button
                onClick={handleUploadToMinio}
                disabled={uploadStatus.isUploading}
                className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto"
              >
                {uploadStatus.isUploading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin mr-2" />
                    Uploading...
                  </>
                ) : (
                  'Upload to MinIO'
                )}
              </button>
            </div>
          )}

          {/* Upload Status */}
          {uploadStatus.error && (
            <div className="text-center text-red-500 text-sm bg-red-50 dark:bg-red-900/20 p-2 rounded">
              Error: {uploadStatus.error}
            </div>
          )}

          {uploadStatus.success && (
            <div className="text-center text-green-600 text-sm bg-green-50 dark:bg-green-900/20 p-2 rounded">
              ✅ Successfully uploaded to MinIO!
            </div>
          )}

          {/* Remove Button */}
          <div className="text-center">
            <button
              onClick={handleRemove}
              className="text-foreground/60 hover:text-foreground p-2 flex items-center justify-center hover:bg-foreground/10 transition-colors mx-auto"
              title="Remove image"
            >
              Remove
            </button>
          </div>
        </div>
      )}

      {/* Image View Modal */}
      <ImageViewModal
        isOpen={isModalOpen}
        imageUrl={image}
        onClose={() => setIsModalOpen(false)}
        title="Uploaded Image"
      />
    </div>
  );
}
