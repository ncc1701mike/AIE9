'use client';

import ChatInterface from '@/components/ChatInterface';
// Adding this Debug Line to check git commit and ensure it works

export default function Home() {
  return (
    <main>
      <div className="background-gradient"></div>
      <div className="background-glow"></div>
      <div className="gradient-wash"></div>
      <div className="gradient-wave"></div>
      <div className="container">
        <ChatInterface />
      </div>
    </main>
  );
}

