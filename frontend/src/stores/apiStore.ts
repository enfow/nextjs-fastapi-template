import { useSession } from 'next-auth/react';
import { create } from 'zustand';

export interface UploadedImage {
  id: string;
  file_name: string;
  original_name: string;
  directory_name: string;
  file_size: number;
  content_type: string;
  url: string;
  uploaded_at: string;
  image_info?: {
    width: number;
    height: number;
    format: string;
  };
}

export interface UploadStatus {
  isUploading: boolean;
  progress: number;
  error: string | null;
  success: boolean;
}

interface ApiStore {
  // Upload status
  uploadStatus: UploadStatus;
  setUploadStatus: (status: Partial<UploadStatus>) => void;
  resetUploadStatus: () => void;

  // Uploaded images management
  uploadedImages: UploadedImage[];
  addUploadedImage: (image: UploadedImage) => void;
  addMultipleUploadedImages: (images: UploadedImage[]) => void;
  removeUploadedImage: (imageId: string) => void;
  clearUploadedImages: () => void;

  // API functions
  uploadSingleImage: (
    file: File,
    directoryName: string,
    description?: string
  ) => Promise<UploadedImage | null>;
  uploadMultipleImages: (
    files: File[],
    directoryName: string,
    description?: string
  ) => Promise<UploadedImage[]>;
  deleteImage: (directoryName: string, fileName: string) => Promise<boolean>;
  getImagesFromDirectory: (directoryName: string) => Promise<UploadedImage[]>;
}

const defaultUploadStatus: UploadStatus = {
  isUploading: false,
  progress: 0,
  error: null,
  success: false,
};

// Helper function to get backend URL
const getBackendUrl = () => {
  return process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
};

// Helper function to get auth token
const getAuthToken = (): string | null => {
  // This will be handled by the component using the store
  return null;
};

export const useApiStore = create<ApiStore>((set, get) => ({
  // Upload status
  uploadStatus: defaultUploadStatus,
  setUploadStatus: (status: Partial<UploadStatus>) =>
    set((state) => ({
      uploadStatus: { ...state.uploadStatus, ...status },
    })),
  resetUploadStatus: () => set({ uploadStatus: defaultUploadStatus }),

  // Uploaded images
  uploadedImages: [],
  addUploadedImage: (image: UploadedImage) =>
    set((state) => ({
      uploadedImages: [...state.uploadedImages, image],
    })),
  addMultipleUploadedImages: (images: UploadedImage[]) =>
    set((state) => ({
      uploadedImages: [...state.uploadedImages, ...images],
    })),
  removeUploadedImage: (imageId: string) =>
    set((state) => ({
      uploadedImages: state.uploadedImages.filter((img) => img.id !== imageId),
    })),
  clearUploadedImages: () => set({ uploadedImages: [] }),

  // API functions
  uploadSingleImage: async (
    file: File,
    directoryName: string,
    description?: string
  ) => {
    const { setUploadStatus } = get();

    // Starting single image upload

    try {
      setUploadStatus({
        isUploading: true,
        progress: 0,
        error: null,
        success: false,
      });

      const formData = new FormData();
      formData.append('file', file);
      formData.append('directory_name', directoryName);
      if (description) {
        formData.append('description', description);
      }

      console.log('🔄 [FRONTEND] FormData created:', {
        fileEntry: formData.get('file'),
        directoryEntry: formData.get('directory_name'),
        descriptionEntry: formData.get('description'),
      });

      const backendUrl = getBackendUrl();
      console.log(
        '🔗 [FRONTEND] Making request to:',
        `${backendUrl}/api/images/upload`
      );

      const response = await fetch(`${backendUrl}/api/images/upload`, {
        method: 'POST',
        body: formData,
        // Note: Don't set Content-Type header, let browser set it with boundary for FormData
      });

      console.log('📡 [FRONTEND] Response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries()),
      });

      setUploadStatus({ progress: 100 });

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ detail: 'Upload failed' }));
        console.error('❌ [FRONTEND] Upload failed:', errorData);
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      console.log('✅ [FRONTEND] Upload successful:', result);

      const uploadedImage: UploadedImage = {
        id: result.file_name, // Using file_name as unique ID
        file_name: result.file_name,
        original_name: result.original_name,
        directory_name: result.directory_name,
        file_size: result.file_size,
        content_type: result.content_type,
        url: result.url,
        uploaded_at: result.uploaded_at,
        image_info: result.image_info,
      };

      setUploadStatus({ isUploading: false, success: true });
      console.log('🎯 [FRONTEND] Single upload complete:', uploadedImage);
      return uploadedImage;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Upload failed';

      // Enhanced error logging
      console.error('❌ [FRONTEND] Single upload error details:', {
        error: error,
        errorMessage: errorMessage,
        errorType: typeof error,
        errorConstructor: error?.constructor?.name,
        errorStack: error instanceof Error ? error.stack : 'No stack trace',
        errorString: String(error),
        errorJSON: JSON.stringify(error, Object.getOwnPropertyNames(error)),
      });

      // Log the specific fetch error if it exists
      if (error instanceof TypeError) {
        console.error('❌ [FRONTEND] This is a TypeError. Full error details:');
        console.error('  - Error message:', error.message);
        console.error('  - Error stack:', error.stack);

        if (error.message.includes('fetch')) {
          console.error(
            '❌ [FRONTEND] This appears to be a network/fetch error. Possible causes:'
          );
          console.error('  - Backend is not accessible from browser');
          console.error('  - CORS issue');
          console.error('  - Network connectivity problem');
          console.error('  - Invalid URL');
        }
      }

      setUploadStatus({
        isUploading: false,
        error: errorMessage,
        success: false,
      });
      return null;
    }
  },

  uploadMultipleImages: async (
    files: File[],
    directoryName: string,
    description?: string
  ) => {
    const { setUploadStatus } = get();

    console.log('🔵 [FRONTEND] Starting bulk image upload:', {
      fileCount: files.length,
      files: files.map((f) => ({ name: f.name, size: f.size, type: f.type })),
      directoryName,
      description,
    });

    try {
      setUploadStatus({
        isUploading: true,
        progress: 0,
        error: null,
        success: false,
      });

      const formData = new FormData();
      files.forEach((file, index) => {
        console.log(
          `📎 [FRONTEND] Adding file ${index + 1}: ${file.name} (${file.size} bytes)`
        );
        formData.append('files', file);
      });
      formData.append('directory_name', directoryName);
      if (description) {
        formData.append('description', description);
      }

      console.log('🔄 [FRONTEND] FormData created with:', {
        filesCount: formData.getAll('files').length,
        directoryEntry: formData.get('directory_name'),
        descriptionEntry: formData.get('description'),
      });

      const backendUrl = getBackendUrl();
      const uploadUrl = `${backendUrl}/api/images/${directoryName}/bulk-upload`;
      console.log('🔗 [FRONTEND] Making bulk upload request to:', uploadUrl);

      // Debug the fetch call parameters
      const fetchOptions = {
        method: 'POST',
        body: formData,
      };
      console.log('🔧 [FRONTEND] Fetch options:', fetchOptions);
      console.log(
        '🔧 [FRONTEND] FormData entries:',
        Array.from(formData.entries())
      );

      console.log('🚀 [FRONTEND] About to call fetch...');
      const response = await fetch(uploadUrl, fetchOptions);

      console.log('📡 [FRONTEND] Bulk upload response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries()),
      });

      setUploadStatus({ progress: 100 });

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ detail: 'Bulk upload failed' }));
        console.error('❌ [FRONTEND] Bulk upload failed:', errorData);
        throw new Error(errorData.detail || 'Bulk upload failed');
      }

      const result = await response.json();
      console.log('📋 [FRONTEND] Bulk upload result:', result);

      if (!result.success && result.errors?.length > 0) {
        console.error(
          '❌ [FRONTEND] Some files failed to upload:',
          result.errors
        );
        throw new Error(
          `Upload failed for some files: ${result.errors.map((e: any) => e.error).join(', ')}`
        );
      }

      const uploadedImages: UploadedImage[] = result.results.map(
        (item: any) => ({
          id: item.file_name,
          file_name: item.file_name,
          original_name: item.original_name,
          directory_name: item.directory_name,
          file_size: item.file_size,
          content_type: item.content_type,
          url: item.url,
          uploaded_at: item.uploaded_at,
          image_info: item.image_info,
        })
      );

      setUploadStatus({ isUploading: false, success: true });
      console.log('🎯 [FRONTEND] Bulk upload complete:', {
        uploadedCount: uploadedImages.length,
        images: uploadedImages.map((img) => img.file_name),
      });
      return uploadedImages;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Bulk upload failed';

      // Enhanced error logging
      console.error('❌ [FRONTEND] Bulk upload error details:', {
        error: error,
        errorMessage: errorMessage,
        errorType: typeof error,
        errorConstructor: error?.constructor?.name,
        errorStack: error instanceof Error ? error.stack : 'No stack trace',
        errorString: String(error),
        errorJSON: JSON.stringify(error, Object.getOwnPropertyNames(error)),
      });

      // Log the specific fetch error if it exists
      if (error instanceof TypeError) {
        console.error('❌ [FRONTEND] This is a TypeError. Full error details:');
        console.error('  - Error message:', error.message);
        console.error('  - Error stack:', error.stack);

        if (error.message.includes('fetch')) {
          console.error(
            '❌ [FRONTEND] This appears to be a network/fetch error. Possible causes:'
          );
          console.error('  - Backend is not accessible from browser');
          console.error('  - CORS issue');
          console.error('  - Network connectivity problem');
          console.error('  - Invalid URL');
        }
      }

      setUploadStatus({
        isUploading: false,
        error: errorMessage,
        success: false,
      });
      return [];
    }
  },

  deleteImage: async (directoryName: string, fileName: string) => {
    try {
      const backendUrl = getBackendUrl();
      const response = await fetch(
        `${backendUrl}/api/images/${directoryName}/${fileName}`,
        {
          method: 'DELETE',
        }
      );

      if (!response.ok) {
        throw new Error('Delete failed');
      }

      return true;
    } catch (error) {
      console.error('Delete image error:', error);
      return false;
    }
  },

  getImagesFromDirectory: async (directoryName: string) => {
    try {
      const backendUrl = getBackendUrl();
      const response = await fetch(`${backendUrl}/api/images/${directoryName}`);

      if (!response.ok) {
        throw new Error('Failed to fetch images');
      }

      const result = await response.json();
      return result.images.map((item: any) => ({
        id: item.file_name,
        file_name: item.file_name,
        original_name: item.original_name,
        directory_name: item.directory_name,
        file_size: item.file_size,
        content_type: item.content_type,
        url: item.url,
        uploaded_at: item.last_modified,
        image_info: {
          width: parseInt(item.image_width) || 0,
          height: parseInt(item.image_height) || 0,
          format: item.image_format || '',
        },
      }));
    } catch (error) {
      console.error('Get images error:', error);
      return [];
    }
  },
}));
