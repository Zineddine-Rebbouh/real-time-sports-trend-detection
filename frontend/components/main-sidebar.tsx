"use client";

import { useState } from "react";
import {
  Search,
  BusIcon as SoccerBall,
  ShoppingBasketIcon as Basketball,
  ClubIcon as Football,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from "@/components/ui/sidebar";
import { DatePickerWithRange } from "@/components/date-range-picker";

export function MainSidebar() {
  const [date, setDate] = useState<{
    from: Date | undefined;
    to: Date | undefined;
  }>({
    from: undefined,
    to: undefined,
  });

  return (
    <Sidebar variant="sidebar" collapsible="icon" side="right">
      <SidebarHeader className="flex flex-col gap-4 p-4">
        <div className="flex items-center gap-2">
          <SoccerBall className="h-5 w-5" />
          <span className="font-semibold">تصفية البيانات</span>
        </div>
      </SidebarHeader>
      <SidebarContent className="p-2">
        <SidebarGroup>
          <SidebarGroupLabel>الرياضة</SidebarGroupLabel>
          <SidebarGroupContent>
            <Select dir="rtl">
              <SelectTrigger className="w-full">
                <SelectValue placeholder="اختر الرياضة" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="football">
                  <div className="flex items-center gap-2">
                    <Football className="h-4 w-4" />
                    <span>كرة القدم</span>
                  </div>
                </SelectItem>
                <SelectItem value="basketball">
                  <div className="flex items-center gap-2">
                    <Basketball className="h-4 w-4" />
                    <span>كرة السلة</span>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup className="mt-6">
          <SidebarGroupLabel>البحث</SidebarGroupLabel>
          <SidebarGroupContent>
            <div className="relative">
              <Search className="absolute right-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="ابحث عن لاعب أو فريق" className="pr-8" />
            </div>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup className="mt-6">
          <SidebarGroupLabel>الفترة الزمنية</SidebarGroupLabel>
          <SidebarGroupContent>
            <DatePickerWithRange date={date} setDate={setDate} />
            <div className="mt-2 flex flex-wrap gap-2">
              <Button variant="outline" size="sm" className="flex-1">
                آخر 7 أيام
              </Button>
              <Button variant="outline" size="sm" className="flex-1">
                آخر 30 يومًا
              </Button>
            </div>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup className="mt-6">
          <Button className="w-full text-white">تطبيق الفلتر</Button>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
