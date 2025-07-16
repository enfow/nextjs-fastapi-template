'use client';

import { useEffect } from 'react';

interface ImageViewModalProps {
  isOpen: boolean;
  imageUrl: string | null;
  onClose: () => void;
  onPrevious?: () => void;
  onNext?: () => void;
  currentIndex?: number;
  totalImages?: number;
  title?: string;
}

export function ImageViewModal({
  isOpen,
  imageUrl,
  onClose,
  onPrevious,
  onNext,
  currentIndex,
  totalImages,
  title = 'Image View',
}: ImageViewModalProps) {
  // Keyboard support
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'Escape':
          onClose();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          onPrevious?.();
          break;
        case 'ArrowRight':
          e.preventDefault();
          onNext?.();
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose, onPrevious, onNext]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen || !imageUrl) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal Content */}
      <div className="relative z-10 max-w-[90vw] max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 bg-background/90 backdrop-blur-sm rounded-t-lg">
          <div className="flex items-center space-x-4">
            <h3 className="text-lg font-semibold text-foreground">{title}</h3>
            {currentIndex !== undefined && totalImages !== undefined && (
              <span className="text-sm text-foreground/60">
                {currentIndex + 1} of {totalImages}
              </span>
            )}
          </div>

          <button
            onClick={onClose}
            className="text-foreground/60 hover:text-foreground p-2 hover:bg-foreground/10 rounded-full transition-colors"
            title="Close"
          >
            ✕
          </button>
        </div>

        {/* Image Container */}
        <div className="relative flex-1 bg-background/90 backdrop-blur-sm rounded-b-lg p-4">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={imageUrl}
            alt="View"
            className="max-w-full max-h-[70vh] object-contain mx-auto block"
          />

          {/* Navigation Buttons for Multi-Image */}
          {onPrevious && onNext && totalImages && totalImages > 1 && (
            <>
              {/* Previous Button */}
              <button
                onClick={onPrevious}
                className="absolute left-4 top-1/2 -translate-y-1/2 bg-black/50 text-white p-3 rounded-full hover:bg-black/70 transition-colors"
                title="Previous image"
                disabled={currentIndex === 0}
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </button>

              {/* Next Button */}
              <button
                onClick={onNext}
                className="absolute right-4 top-1/2 -translate-y-1/2 bg-black/50 text-white p-3 rounded-full hover:bg-black/70 transition-colors"
                title="Next image"
                disabled={currentIndex === totalImages - 1}
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
