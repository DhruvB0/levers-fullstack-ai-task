import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Debt Collection Assistant',
  description: 'AI-powered compliance copilot for debt collection agents',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full">{children}</body>
    </html>
  );
}
