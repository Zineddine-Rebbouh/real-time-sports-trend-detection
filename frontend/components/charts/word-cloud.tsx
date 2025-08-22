"use client";

import { useEffect, useRef } from "react";
import { useTheme } from "next-themes";

interface WordCloudItem {
  word: string;
  count: number;
}

interface WordCloudProps {
  data:
    | WordCloudItem[]
    | Array<{ entity_text: string; count: number; trend_details?: any }>;
}

interface WordPosition {
  text: string;
  x: number;
  y: number;
  width: number;
  height: number;
  fontSize: number;
}

export function WordCloud({ data }: WordCloudProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { theme } = useTheme();

  const drawWordCloud = () => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas dimensions
    canvas.width = canvas.offsetWidth;
    canvas.height = 400;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Set text properties
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "12px Cairo, sans-serif"; // Default font for measurement

    // Map data to the format used for rendering
    const words = data.map((item) => ({
      text: "entity_text" in item ? item.entity_text : item.word,
      value: item.count,
    }));

    // Calculate total value for normalization
    const totalValue = words.reduce((sum, word) => sum + word.value, 0);

    if (totalValue === 0) return; // Avoid division by zero

    // Sort words by value (largest first)
    const sortedWords = [...words].sort((a, b) => b.value - a.value);

    // Colors based on theme
    const colors =
      theme === "dark"
        ? ["#60a5fa", "#4ade80", "#f97316", "#a78bfa", "#f43f5e"]
        : ["#2563eb", "#16a34a", "#ea580c", "#7c3aed", "#e11d48"];

    // Place words randomly with collision detection
    const placedWords: WordPosition[] = [];
    const padding = 5; // Padding to reduce overlap
    const maxAttempts = 100; // Max attempts to place a word

    sortedWords.forEach((word, index) => {
      // Calculate font size based on word value (normalized)
      const fontSize = 12 + (word.value / totalValue) * 60;
      ctx.font = `${fontSize}px Cairo, sans-serif`;

      // Measure text dimensions
      const metrics = ctx.measureText(word.text);
      const textWidth = metrics.width;
      const textHeight = fontSize; // Approximate height

      let placed = false;
      let attempts = 0;

      while (!placed && attempts < maxAttempts) {
        // Random position within canvas bounds
        const x =
          Math.random() * (canvas.width - textWidth - padding * 2) +
          textWidth / 2 +
          padding;
        const y =
          Math.random() * (canvas.height - textHeight - padding * 2) +
          textHeight / 2 +
          padding;

        // Check for collisions with already placed words
        const collides = placedWords.some((placedWord) => {
          const dx = Math.abs(placedWord.x - x);
          const dy = Math.abs(placedWord.y - y);
          const minDistanceX = (placedWord.width + textWidth) / 2 + padding;
          const minDistanceY = (placedWord.height + textHeight) / 2 + padding;
          return dx < minDistanceX && dy < minDistanceY;
        });

        if (!collides) {
          // Place the word
          ctx.fillStyle = colors[index % colors.length];
          ctx.fillText(word.text, x, y);

          // Store position for collision detection
          placedWords.push({
            text: word.text,
            x,
            y,
            width: textWidth,
            height: textHeight,
            fontSize,
          });
          placed = true;
        }

        attempts++;
      }

      if (!placed) {
        console.warn(`Could not place word: ${word.text}`);
      }
    });
  };

  useEffect(() => {
    drawWordCloud();

    // Handle window resize
    const handleResize = () => {
      if (canvasRef.current) {
        drawWordCloud(); // Redraw the word cloud on resize
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [theme, data]); // Re-render when theme or data changes

  return (
    <div className="w-full h-[400px] relative">
      <canvas ref={canvasRef} className="w-full h-full" />
    </div>
  );
}
