"use client";

import { Line, LineChart, CartesianGrid, XAxis, YAxis } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

// Helper to convert ISO date to Arabic date string (e.g., "٢٢ إبريل")
function formatArabicDate(isoDate: string) {
  const months = [
    "يناير",
    "فبراير",
    "مارس",
    "إبريل",
    "مايو",
    "يونيو",
    "يوليو",
    "أغسطس",
    "سبتمبر",
    "أكتوبر",
    "نوفمبر",
    "ديسمبر",
  ];
  const date = new Date(isoDate);
  const day = date.getDate().toLocaleString("ar-EG");
  const month = months[date.getMonth()];
  return `${day} ${month}`;
}

// Raw trend data from the prompt
const playerTrend = [
  { date: "2025-04-22", mentions: 1 },
  { date: "2025-04-23", mentions: 2 },
  { date: "2025-04-24", mentions: 3 },
  { date: "2025-04-25", mentions: 3 },
  { date: "2025-04-26", mentions: 4 },
  { date: "2025-04-27", mentions: 5 },
  { date: "2025-04-28", mentions: 7 },
];
const teamTrend = [
  { date: "2025-04-22", mentions: 1 },
  { date: "2025-04-23", mentions: 2 },
  { date: "2025-04-24", mentions: 2 },
  { date: "2025-04-25", mentions: 3 },
  { date: "2025-04-26", mentions: 4 },
  { date: "2025-04-27", mentions: 5 },
  { date: "2025-04-28", mentions: 5 },
];
const competitionTrend = [
  { date: "2025-04-22", mentions: 2 },
  { date: "2025-04-23", mentions: 3 },
  { date: "2025-04-24", mentions: 4 },
  { date: "2025-04-25", mentions: 3 },
  { date: "2025-04-26", mentions: 5 },
  { date: "2025-04-27", mentions: 6 },
  { date: "2025-04-28", mentions: 7 },
];

// Merge the trends by date
const data = competitionTrend.map((c, i) => ({
  date: formatArabicDate(c.date),
  الدوري_الإنجليزي_الممتاز: c.mentions,
  محمد_صلاح: playerTrend[i]?.mentions ?? 0,
  ليفربول: teamTrend[i]?.mentions ?? 0,
}));

export function HashtagChart() {
  return (
    <ChartContainer
      config={{
        الدوري_الإنجليزي_الممتاز: {
          label: "#الدوري_الإنجليزي",
          color: "hsl(var(--chart-1))",
        },
        محمد_صلاح: {
          label: "#محمد_صلاح",
          color: "hsl(var(--chart-2))",
        },
        ليفربول: {
          label: "#ليفربول",
          color: "hsl(var(--chart-3))",
        },
      }}
      className="aspect-[4/3] w-full"
    >
      <LineChart
        data={data}
        margin={{
          top: 20,
          right: 30,
          left: 20,
          bottom: 10,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis
          dataKey="date"
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12 }}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => `${value}`}
        />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Line
          type="monotone"
          dataKey="الدوري_الإنجليزي_الممتاز"
          stroke="var(--color-الدوري_الإنجليزي_الممتاز)"
          strokeWidth={2}
          activeDot={{ r: 8 }}
        />
        <Line
          type="monotone"
          dataKey="محمد_صلاح"
          stroke="var(--color-محمد_صلاح)"
          strokeWidth={2}
          activeDot={{ r: 8 }}
        />
        <Line
          type="monotone"
          dataKey="ليفربول"
          stroke="var(--color-ليفربول)"
          strokeWidth={2}
          activeDot={{ r: 8 }}
        />
      </LineChart>
    </ChartContainer>
  );
}
