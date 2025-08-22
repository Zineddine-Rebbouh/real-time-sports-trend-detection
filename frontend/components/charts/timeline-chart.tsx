"use client";

import {
  Line,
  LineChart,
  CartesianGrid,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface TrendDetail {
  date: string;
  mentions: number;
}

interface TimelineChartProps {
  data: TrendDetail[];
}

export function TimelineChart({ data }: TimelineChartProps) {
  const chartData = data.map((item) => ({
    ...item,
    formattedDate: new Date(item.date).toLocaleDateString("ar-SA", {
      day: "numeric",
      month: "short",
    }),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart
        data={chartData}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="formattedDate"
          tickMargin={10}
          style={{ fontSize: "12px" }}
        />
        <YAxis
          style={{ fontSize: "12px" }}
          tickFormatter={(value) => value.toLocaleString("ar-SA")}
        />
        <Tooltip
          labelFormatter={(label) => `التاريخ: ${label}`}
          formatter={(value) => [
            value.toLocaleString("ar-SA"),
            "عدد المنشورات",
          ]}
        />
        <Line
          type="monotone"
          dataKey="mentions"
          stroke="#4b9afa"
          strokeWidth={2}
          dot={{ r: 4 }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
