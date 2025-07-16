'use client';

import { useDefaultStore } from '@/stores/defaultStore';

export default function ExamplePage() {
  const { exampleValue } = useDefaultStore();
  return (
    <div>
      <h1>Example Page</h1>
      <p className="text-lg text-foreground/80">{exampleValue}</p>
    </div>
  );
}
