"use client";

import { Cell, Pie, PieChart } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

const data = [
  { name: "إيجابي", value: 75 },
  { name: "محايد", value: 15 },
  { name: "سلبي", value: 10 },
];

const COLORS = [
  "hsl(var(--chart-2))",
  "hsl(var(--chart-1))",
  "hsl(var(--chart-3))",
];

interface SentimentAnalysis {
  positive: number;
  negative: number;
  neutral: number;
}

interface SentimentDonutChartProps {
  data: SentimentAnalysis;
}

export function SentimentDonutChart({ data }: SentimentDonutChartProps) {
  const chartData = [
    { name: "إيجابي", value: data.positive },
    { name: "محايد", value: data.neutral },
    { name: "سلبي", value: data.negative },
  ];

  return (
    <ChartContainer
      config={{
        إيجابي: {
          label: "إيجابي",
          color: COLORS[0],
        },
        محايد: {
          label: "محايد",
          color: COLORS[1],
        },
        سلبي: {
          label: "سلبي",
          color: COLORS[2],
        },
      }}
      className="aspect-[4/3] w-full"
    >
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={80}
          fill="#8884d8"
          paddingAngle={5}
          dataKey="value"
          label={({ name, percent }) =>
            `${name} ${(percent * 100).toFixed(0)}%`
          }
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <ChartTooltip content={<ChartTooltipContent />} />
      </PieChart>
    </ChartContainer>
  );
}
