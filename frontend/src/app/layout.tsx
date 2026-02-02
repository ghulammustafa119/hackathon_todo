import '../styles/globals.css';

export const metadata = {
  title: 'Todo Dashboard',
  description: 'A todo application with AI assistance',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}