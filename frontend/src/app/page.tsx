'use client';

import { useSession } from 'next-auth/react';
import Link from 'next/link';

export default function Home() {
  const { data: session } = useSession();

  return (
    <div className="min-h-screen bg-background py-8">
      <h1 className="text-4xl font-bold text-foreground mb-8">
        Welcome to Image Uploader App
      </h1>

      {session ? (
        <div>
          <p className="text-lg text-foreground/80 mb-6">
            Welcome back,{' '}
            {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
            {(session.user as any)?.username || session.user?.name}! Ready to
            upload some images?
          </p>
          <div className="space-y-4">
            <div>
              <Link
                href="/image-uploader/single-image"
                className="bg-primary text-primary-foreground px-6 py-3 rounded-md hover:bg-primary/90 transition-colors inline-block"
              >
                Single Image Uploader
              </Link>
            </div>
            <div>
              <Link
                href="/image-uploader/multi-image"
                className="bg-secondary text-secondary-foreground px-6 py-3 rounded-md hover:bg-secondary/80 transition-colors inline-block"
              >
                Multi-Image Gallery
              </Link>
            </div>
          </div>
        </div>
      ) : (
        <div>
          <p className="text-lg text-foreground/80 mb-6">
            Please log in to access the image uploaders.
          </p>
          <Link
            href="/login"
            className="bg-primary text-primary-foreground px-6 py-3 rounded-md hover:bg-primary/90 transition-colors inline-block"
          >
            Login
          </Link>
        </div>
      )}
    </div>
  );
}
