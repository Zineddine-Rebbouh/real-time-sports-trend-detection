"use client";

import { Cell, Pie, PieChart } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

const COLORS = [
  "hsl(var(--chart-2))",
  "hsl(var(--chart-1))",
  "hsl(var(--chart-3))",
];

interface SentimentData {
  positive: number;
  negative: number;
  neutral: number;
}

interface SentimentChartProps {
  data: SentimentData;
}

interface ChartData {
  name: string;
  value: number;
}

export function SentimentChart({ data }: SentimentChartProps) {
  // Transform the data prop into the format expected by recharts
  const chartData: ChartData[] = [
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
          labelLine={false}
          outerRadius={80}
          fill="#8884d8"
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
