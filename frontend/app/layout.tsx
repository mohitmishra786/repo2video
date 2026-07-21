import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'repo2video - Turn GitHub repos into narrated videos',
  description: 'Paste any GitHub URL, get a 1080p narrated code walkthrough video. Open source. Free.',
  openGraph: {
    title: 'repo2video - Turn GitHub repos into narrated videos',
    description: 'Paste any GitHub URL, get a narrated code walkthrough video in minutes.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0d1117] text-[#c9d1d9] antialiased">
        {children}
      </body>
    </html>
  );
}
