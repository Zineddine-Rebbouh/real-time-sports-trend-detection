"use client";

import { Line, LineChart, CartesianGrid, XAxis, YAxis } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

import { TrendData } from "@/hooks/use-filtered-trends";

interface MentionChartProps {
  data: TrendData[];
}

export function MentionChart({ data }: MentionChartProps) {
  console.log("MentionChart", data);
  return (
    <ChartContainer
      config={{
        mentions: {
          label: "المنشورات",
          color: "hsl(var(--chart-1))",
        },
      }}
      className="aspect-[4/3] w-full"
    >
      <LineChart
        data={data.flatMap((trend) => trend.trend_details)}
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
          dataKey="mentions"
          stroke="var(--color-mentions)"
          strokeWidth={2}
          activeDot={{ r: 8 }}
        />
      </LineChart>
    </ChartContainer>
  );
}
