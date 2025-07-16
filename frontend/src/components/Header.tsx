'use client';

import { signOut, useSession } from 'next-auth/react';
import Link from 'next/link';

const TITLE = 'Next.js Template';

export function Header() {
  const { data: session } = useSession();
  return (
    <header className="bg-primary border-b border-foreground/10 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex-1"></div>
          <div className="flex-1 flex justify-center">
            <h1 className="text-xl font-bold text-primary-foreground">
              <Link href="/" className="hover:opacity-80 transition-opacity">
                {TITLE}
              </Link>
            </h1>
          </div>
          <div className="flex-1 flex justify-end">
            <nav className="flex items-center space-x-6">
              {session ? (
                <>
                  <Link
                    href="/"
                    className="text-primary-foreground/80 hover:text-primary-foreground transition-colors"
                  >
                    Home
                  </Link>
                  <Link
                    href="/image-uploader/single-image"
                    className="text-primary-foreground/80 hover:text-primary-foreground transition-colors"
                  >
                    Single Image
                  </Link>
                  <Link
                    href="/image-uploader/multi-image"
                    className="text-primary-foreground/80 hover:text-primary-foreground transition-colors"
                  >
                    Multi Images
                  </Link>
                  <span className="text-primary-foreground/80 text-sm">
                    Welcome,{' '}
                    {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                    {(session.user as any)?.username || session.user?.name}
                  </span>
                  <button
                    onClick={() => signOut()}
                    className="text-primary-foreground/80 hover:text-primary-foreground transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/"
                    className="text-primary-foreground/80 hover:text-primary-foreground transition-colors"
                  >
                    Home
                  </Link>
                  <Link
                    href="/login"
                    className="text-primary-foreground/80 hover:text-primary-foreground transition-colors"
                  >
                    Login
                  </Link>
                </>
              )}
            </nav>
          </div>
        </div>
      </div>
    </header>
  );
}
