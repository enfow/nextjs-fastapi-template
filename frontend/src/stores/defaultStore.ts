import { create } from 'zustand';

interface DefaultStore {
  exampleValue: string;
  setExampleValue: (value: string) => void;
  uploadedImage: string | null;
  setUploadedImage: (image: string | null) => void;
  removeUploadedImage: () => void;
  uploadedImages: string[];
  addUploadedImage: (image: string) => void;
  addMultipleImages: (images: string[]) => void;
  removeUploadedImageAt: (index: number) => void;
  clearAllImages: () => void;
  reorderImages: (fromIndex: number, toIndex: number) => void;
}

export const useDefaultStore = create<DefaultStore>((set) => ({
  exampleValue: '',
  setExampleValue: (value: string) => set({ exampleValue: value }),
  uploadedImage: null,
  setUploadedImage: (image: string | null) => set({ uploadedImage: image }),
  removeUploadedImage: () => set({ uploadedImage: null }),
  uploadedImages: [],
  addUploadedImage: (image: string) =>
    set((state) => ({ uploadedImages: [...state.uploadedImages, image] })),
  addMultipleImages: (images: string[]) =>
    set((state) => ({ uploadedImages: [...state.uploadedImages, ...images] })),
  removeUploadedImageAt: (index: number) =>
    set((state) => ({
      uploadedImages: state.uploadedImages.filter((_, i) => i !== index),
    })),
  clearAllImages: () => set({ uploadedImages: [] }),
  reorderImages: (fromIndex: number, toIndex: number) =>
    set((state) => {
      const newImages = [...state.uploadedImages];
      const [removed] = newImages.splice(fromIndex, 1);
      newImages.splice(toIndex, 0, removed);
      return { uploadedImages: newImages };
    }),
}));
