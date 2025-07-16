'use client';

import { useRef, useState } from 'react';

import { ImageViewModal } from './ImageViewModal';

interface MultiImageUploaderProps {
  images: string[];
  onImagesAdd: (images: string[]) => void;
  onImageRemove: (index: number) => void;
  onClearAll: () => void;
  maxImages?: number;
}

export function MultiImageUploader({
  images,
  onImagesAdd,
  onImageRemove,
  onClearAll,
  maxImages = 10,
}: MultiImageUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFilesSelect = (files: FileList) => {
    const remainingSlots = maxImages - images.length;
    const filesToProcess = Array.from(files).slice(0, remainingSlots);

    const imagePromises = filesToProcess
      .filter((file) => file.type.startsWith('image/'))
      .map((file) => {
        return new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onload = (e) => resolve(e.target?.result as string);
          reader.readAsDataURL(file);
        });
      });

    Promise.all(imagePromises).then(onImagesAdd);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      handleFilesSelect(files);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files) {
      handleFilesSelect(files);
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
    if (images.length < maxImages) {
      fileInputRef.current?.click();
    }
  };

  const canAddMore = images.length < maxImages;

  const handleImageClick = (index: number) => {
    setCurrentImageIndex(index);
    setIsModalOpen(true);
  };

  const handlePreviousImage = () => {
    setCurrentImageIndex((prev) => (prev > 0 ? prev - 1 : images.length - 1));
  };

  const handleNextImage = () => {
    setCurrentImageIndex((prev) => (prev < images.length - 1 ? prev + 1 : 0));
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Upload Area */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
          transition-all duration-200 mb-6
          ${
            isDragOver
              ? 'border-primary bg-primary/5'
              : canAddMore
                ? 'border-foreground/30 hover:border-primary hover:bg-primary/5'
                : 'border-foreground/20 bg-foreground/5 cursor-not-allowed'
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
          multiple
          onChange={handleFileInputChange}
          className="hidden"
          disabled={!canAddMore}
        />

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
          {canAddMore ? (
            <>
              <p className="text-lg font-medium text-foreground mb-2">
                Click to upload images or drag and drop
              </p>
              <p className="text-sm text-foreground/60">
                Select multiple images at once
              </p>
              <p className="text-xs text-foreground/40 mt-2">
                PNG, JPG, GIF • {images.length}/{maxImages} images
              </p>
            </>
          ) : (
            <>
              <p className="text-lg font-medium text-foreground/60 mb-2">
                Maximum images reached
              </p>
              <p className="text-sm text-foreground/40">
                {images.length}/{maxImages} images uploaded
              </p>
            </>
          )}
        </div>
      </div>

      {/* Images Gallery */}
      {images.length > 0 && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-foreground">
              Uploaded Images ({images.length})
            </h3>
            <button
              onClick={onClearAll}
              className="text-foreground/60 hover:text-foreground p-2 flex items-center justify-center hover:bg-foreground/10 transition-colors"
              title="Clear all images"
            >
              Clear
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {images.map((image, index) => (
              <div
                key={index}
                className="relative group aspect-square bg-foreground/5 rounded-lg overflow-hidden border border-foreground/10"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={image}
                  alt={`Uploaded ${index + 1}`}
                  className="w-full h-full object-cover transition-transform group-hover:scale-105"
                />
                <div
                  className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors cursor-pointer"
                  onClick={() => handleImageClick(index)}
                >
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onImageRemove(index);
                    }}
                    className="absolute top-1 right-1 bg-black/50 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-black/70 transition-colors opacity-0 group-hover:opacity-100"
                  >
                    ✕
                  </button>
                </div>
                <div className="absolute bottom-1 left-1 bg-black/50 text-white text-xs px-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                  {index + 1}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {images.length === 0 && (
        <div className="text-center py-8">
          <p className="text-foreground/60">No images uploaded yet</p>
          <p className="text-sm text-foreground/40 mt-1">
            Upload your first image to get started
          </p>
        </div>
      )}

      {/* Image View Modal */}
      <ImageViewModal
        isOpen={isModalOpen}
        imageUrl={images[currentImageIndex] || null}
        onClose={() => setIsModalOpen(false)}
        onPrevious={handlePreviousImage}
        onNext={handleNextImage}
        currentIndex={currentImageIndex}
        totalImages={images.length}
        title="Gallery Image"
      />
    </div>
  );
}
