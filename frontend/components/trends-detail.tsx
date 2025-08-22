"use client";

import { useState } from "react";
import Image from "next/image";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MentionChart } from "@/components/charts/mention-chart";
import { SentimentDonutChart } from "@/components/charts/sentiment-donut-chart";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { EntityType } from "@/hooks/use-detailed-stats";
import { LoadingState } from "@/components/loading-state";
import useFilteredTrends, { SportType } from "@/hooks/use-filtered-trends";

export default function TrendsDetail() {
  const [entityType, setEntityType] = useState<EntityType>("PLAYER");
  const [selectedSport, setSelectedSport] = useState<SportType>("كرة_القدم");

  const {
    data: stats,
    loading,
    error,
  } = useFilteredTrends(selectedSport, entityType);

  if (loading) {
    return <LoadingState />;
  }

  if (error || !stats) {
    return (
      <div className="w-full text-center text-red-500">
        حدث خطأ في تحميل البيانات
      </div>
    );
  }

  return (
    <div className="w-full space-y-4">
      <div className="space-y-4 w-full">
        <div className="flex items-center justify-between w-full">
          <h2 className="text-3xl font-bold tracking-tight">
            تفاصيل الاتجاهات
          </h2>
          <Tabs
            value={entityType}
            onValueChange={(value) => setEntityType(value as EntityType)}
          >
            <TabsList>
              <TabsTrigger value="PLAYER">لاعب</TabsTrigger>
              <TabsTrigger value="TEAM">فريق</TabsTrigger>
              <TabsTrigger value="COMPETITION">منافسة</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <div className="flex justify-end gap-2">
          <Tabs
            value={selectedSport}
            onValueChange={(value) => setSelectedSport(value as SportType)}
            className="w-auto"
          >
            <TabsList>
              <TabsTrigger value="كرة_القدم">كرة القدم</TabsTrigger>
              <TabsTrigger value="كرة_السلة">كرة السلة</TabsTrigger>
              <TabsTrigger value="تنس">تنس</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </div>

      <Card className="w-full">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-6 items-center md:items-start w-full">
            <div className="w-32 h-32 relative rounded-full overflow-hidden border-4 border-primary/20 flex-shrink-0">
              <Image
                src="/placeholder.svg?height=128&width=128"
                alt={stats.entity_text}
                width={128}
                height={128}
                className="object-cover"
              />
            </div>
            <div className="text-center md:text-right">
              <h3 className="text-2xl font-bold">{stats.entity_text}</h3>
              <p className="text-muted-foreground">
                {entityType === "PLAYER"
                  ? "لاعب"
                  : entityType === "TEAM"
                  ? "فريق"
                  : "منافسة"}
              </p>
            </div>
            <div className="flex-1 grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4 md:mt-0 md:mr-auto">
              <div className="bg-muted rounded-lg p-3 text-center">
                <div className="text-2xl font-bold">{stats?.count}</div>
                <div className="text-xs text-muted-foreground">
                  إجمالي المنشورات
                </div>
              </div>
              <div className="bg-muted rounded-lg p-3 text-center">
                <div className="text-2xl font-bold">
                  {Math.round(
                    (stats?.sentiment?.positive / stats?.count) * 100
                  )}
                  %
                </div>
                <div className="text-xs text-muted-foreground">
                  مشاعر إيجابية
                </div>
              </div>
              <div className="bg-muted rounded-lg p-3 text-center">
                <div className="text-2xl font-bold">
                  {Math.round(
                    (stats?.trend_details[stats?.trend_details?.length - 1]
                      .mentions /
                      (stats?.trend_details[stats?.trend_details?.length - 2]
                        .mentions || 1) -
                      1) *
                      100
                  )}
                  %
                </div>
                <div className="text-xs text-muted-foreground">
                  زيادة أسبوعية
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-7 gap-4 w-full">
        <Card className="lg:col-span-4 w-full">
          <CardHeader>
            <CardTitle>المنشورات عبر الزمن</CardTitle>
            <CardDescription>
              تطور عدد المنشورات خلال الفترة المحددة
            </CardDescription>
          </CardHeader>
          <CardContent>
            <MentionChart data={[stats]} />
          </CardContent>
        </Card>
        <Card className="lg:col-span-3 w-full">
          <CardHeader>
            <CardTitle>تحليل المشاعر</CardTitle>
            <CardDescription>توزيع المشاعر في المنشورات</CardDescription>
          </CardHeader>
          <CardContent>
            <SentimentDonutChart data={stats?.sentiment} />
          </CardContent>
        </Card>
      </div>

      <Card className="w-full">
        <CardHeader>
          <CardTitle>عينة من المنشورات</CardTitle>
          <CardDescription>
            آخر المنشورات المتعلقة بـ {stats?.entity_text}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px] rounded-md border p-4 w-full">
            <div className="space-y-4 w-full">
              {stats.sample_comments.map((post, i) => {
                const postDate = new Date(post.date);
                const now = new Date();
                const diffInMs = now.getTime() - postDate.getTime();
                const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
                const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
                const timeAgo =
                  diffInDays >= 1
                    ? `منذ ${diffInDays} يوم`
                    : `منذ ${diffInHours} ساعة`;

                return (
                  <div
                    key={i}
                    className="flex gap-4 p-4 rounded-lg border w-full"
                  >
                    <Avatar className="flex-shrink-0">
                      <AvatarImage
                        src={`/placeholder.svg?height=40&width=40&text=${
                          i + 1
                        }`}
                      />
                      <AvatarFallback>مستخدم</AvatarFallback>
                    </Avatar>
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{post?.author_name}</span>
                        <span className="text-xs text-muted-foreground">
                          {timeAgo}
                        </span>
                        <span
                          className={`text-xs rounded-full px-2 py-0.5 ${
                            post.sentiment === "positive"
                              ? "bg-green-100 text-green-800"
                              : post.sentiment === "negative"
                              ? "bg-red-100 text-red-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {post.sentiment === "positive"
                            ? "إيجابي"
                            : post.sentiment === "negative"
                            ? "سلبي"
                            : "محايد"}
                        </span>
                      </div>
                      <p>{post.text}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
