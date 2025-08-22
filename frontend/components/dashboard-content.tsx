"use client";

import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { HashtagChart } from "@/components/charts/hashtag-chart";
import { SentimentChart } from "@/components/charts/sentiment-chart";
import { WordCloud } from "@/components/charts/word-cloud";
import { StatsCard } from "@/components/stats-card";
import { User, MessageSquare, TrendingUp } from "lucide-react";
import { useDashboardStats } from "@/hooks/use-dashboard-stats";
import { LoadingState } from "@/components/loading-state";

export function DashboardContent() {
  const { stats, loading, error } = useDashboardStats();

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <div className="w-full text-center text-red-500">
        حدث خطأ في تحميل البيانات
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between w-full">
        <h2 className="text-3xl font-bold tracking-tight">لوحة التحكم</h2>
        {/* <Tabs defaultValue="day">
          <TabsList>
            <TabsTrigger value="day">اليوم</TabsTrigger>
            <TabsTrigger value="week">الأسبوع</TabsTrigger>
            <TabsTrigger value="month">الشهر</TabsTrigger>
          </TabsList>
        </Tabs> */}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
        <StatsCard
          title="أكثر رياضي ذكرًا"
          value={stats.most_mentioned_player.entity_text}
          description={`${stats.most_mentioned_player.count} منشور`}
          icon={<User className="h-4 w-4 text-muted-foreground" />}
        />
        <StatsCard
          title="أكثر هاشتاغ تداولًا"
          value={stats.most_popular_hashtag}
          description="308 منشور"
          icon={<TrendingUp className="h-4 w-4 text-muted-foreground" />}
        />
        <StatsCard
          title="إجمالي المنشورات"
          value={stats.total_posts.toString()}
          description="زيادة ٢٠٪ عن الأسبوع الماضي"
          icon={<MessageSquare className="h-4 w-4 text-muted-foreground" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-7 gap-4 w-full">
        <Card className="lg:col-span-4 w-full">
          <CardHeader>
            <CardTitle>شعبية الهاشتاغات</CardTitle>
            <CardDescription>
              تطور شعبية الهاشتاغات خلال الفترة المحددة
            </CardDescription>
          </CardHeader>
          <CardContent>
            <HashtagChart />
          </CardContent>
        </Card>
        <Card className="lg:col-span-3 w-full">
          <CardHeader>
            <CardTitle>تحليل المشاعر</CardTitle>
            <CardDescription>توزيع المشاعر في المنشورات</CardDescription>
          </CardHeader>
          <CardContent>
            <SentimentChart data={stats.sentiment_analysis} />
          </CardContent>
        </Card>
      </div>

      <Card className="w-full">
        <CardHeader>
          <CardTitle>سحابة الكلمات</CardTitle>
          <CardDescription>الكلمات الأكثر تداولًا في المنشورات</CardDescription>
        </CardHeader>
        <CardContent>
          <WordCloud data={stats.word_cloud} />
        </CardContent>
      </Card>
    </div>
  );
}
