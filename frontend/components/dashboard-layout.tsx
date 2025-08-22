"use client";

import type React from "react";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  FileText,
  Home,
  Info,
  Menu,
  Moon,
  Search,
  BusIcon as SoccerBall,
  Sun,
  X,
  User,
} from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarSeparator,
} from "@/components/ui/sidebar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { DatePickerWithRange } from "@/components/date-range-picker";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/hooks/use-auth";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { setTheme, theme } = useTheme();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <div className="flex min-h-screen flex-col w-full">
      {/* Header */}
      <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
        <div className="flex items-center gap-2 md:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileMenuOpen(true)}
          >
            <Menu className="h-5 w-5" />
            <span className="sr-only">فتح القائمة</span>
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <SoccerBall className="h-6 w-6" />
          <span className="font-bold">اتجاهات رياضية</span>
        </div>
        <nav className="hidden md:flex md:gap-4 lg:gap-6 mr-6">
          <Link
            href="/"
            className={`text-sm font-medium ${
              pathname === "/" ? "text-primary" : "text-muted-foreground"
            } transition-colors hover:text-primary`}
          >
            الرئيسية
          </Link>
          <Link
            href="/trends"
            className={`text-sm font-medium ${
              pathname === "/trends" ? "text-primary" : "text-muted-foreground"
            } transition-colors hover:text-primary`}
          >
            لوحة التحكم
          </Link>
          <Link
            href="/reports"
            className={`text-sm font-medium ${
              pathname === "/reports-fx"
                ? "text-primary"
                : "text-muted-foreground"
            } transition-colors hover:text-primary`}
          >
            تقارير
          </Link>
          <Link
            href="/about"
            className={`text-sm font-medium ${
              pathname === "/about" ? "text-primary" : "text-muted-foreground"
            } transition-colors hover:text-primary`}
          >
            حول المشروع
          </Link>
        </nav>
        <div className="mr-auto flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">تبديل المظهر</span>
          </Button>

          {isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="relative h-8 w-8 rounded-full"
                >
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user?.image} alt={user?.name} />
                    <AvatarFallback>
                      {user?.name?.charAt(0) || "U"}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {user?.name}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {user?.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/profile">الملف الشخصي</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings">الإعدادات</Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout}>
                  تسجيل الخروج
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <div className="flex gap-2">
              <Button variant="ghost" asChild>
                <Link href="/login">تسجيل الدخول</Link>
              </Button>
              <Button asChild>
                <Link href="/signup">إنشاء حساب</Link>
              </Button>
            </div>
          )}
        </div>
      </header>

      {/* Mobile Menu */}
      <div
        className={`fixed inset-0 z-50 bg-background md:hidden ${
          mobileMenuOpen ? "block" : "hidden"
        }`}
      >
        <div className="flex h-16 items-center gap-4 border-b bg-background px-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileMenuOpen(false)}
          >
            <X className="h-5 w-5" />
            <span className="sr-only">إغلاق القائمة</span>
          </Button>
          <div className="flex items-center gap-2">
            <SoccerBall className="h-6 w-6" />
            <span className="font-bold">اتجاهات رياضية</span>
          </div>
        </div>
        <nav className="grid gap-2 p-4">
          <Link
            href="/"
            className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium ${
              pathname === "/"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground"
            } transition-colors hover:text-primary`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <Home className="h-5 w-5" />
            الرئيسية
          </Link>
          <Link
            href="/trends"
            className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium ${
              pathname === "/trends"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground"
            } transition-colors hover:text-primary`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <BarChart3 className="h-5 w-5" />
            لوحة التحكم
          </Link>
          <Link
            href="/reports"
            className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium ${
              pathname === "/reports"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground"
            } transition-colors hover:text-primary`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <FileText className="h-5 w-5" />
            تقارير
          </Link>
          <Link
            href="/about"
            className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium ${
              pathname === "/about"
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground"
            } transition-colors hover:text-primary`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <Info className="h-5 w-5" />
            حول المشروع
          </Link>
          {!isAuthenticated && (
            <>
              <DropdownMenuSeparator />
              <Link
                href="/login"
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
                onClick={() => setMobileMenuOpen(false)}
              >
                <User className="h-5 w-5" />
                تسجيل الدخول
              </Link>
              <Link
                href="/signup"
                className="flex items-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm text-white font-medium text-primary-foreground"
                onClick={() => setMobileMenuOpen(false)}
              >
                إنشاء حساب
              </Link>
            </>
          )}
        </nav>
      </div>

      {/* Main Content with Sidebar */}
      <div className="flex flex-1 w-full">
        {/* <Sidebar collapsible="icon" side="right">
          <SidebarHeader className="shrink-0">
            <div className="flex items-center justify-between p-2">
              <span className="text-sm font-medium">تصفية البيانات</span>
            </div>
          </SidebarHeader>
          <SidebarContent className="overflow-hidden">
            <SidebarGroup>
              <SidebarGroupLabel>الرياضة</SidebarGroupLabel>
              <SidebarGroupContent>
                <div className="space-y-4 p-2">
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="اختر الرياضة" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="football">كرة القدم</SelectItem>
                      <SelectItem value="basketball">كرة السلة</SelectItem>
                      <SelectItem value="tennis">التنس</SelectItem>
                      <SelectItem value="handball">كرة اليد</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </SidebarGroupContent>
            </SidebarGroup>
            <SidebarSeparator />
            <SidebarGroup>
              <SidebarGroupLabel>البحث</SidebarGroupLabel>
              <SidebarGroupContent>
                <div className="p-2">
                  <div className="relative">
                    <Search className="absolute right-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="ابحث عن لاعب أو فريق"
                      className="pr-8"
                    />
                  </div>
                </div>
              </SidebarGroupContent>
            </SidebarGroup>
            <SidebarSeparator />
            <SidebarGroup>
              <SidebarGroupLabel>الفترة الزمنية</SidebarGroupLabel>
              <SidebarGroupContent>
                <div className="p-2 space-y-4">
                  <DatePickerWithRange />
                  <div className="flex flex-wrap gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      آخر 7 أيام
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1">
                      آخر 30 يومًا
                    </Button>
                  </div>
                </div>
              </SidebarGroupContent>
            </SidebarGroup>
            <SidebarSeparator />
          </SidebarContent>
          <SidebarFooter>
            <div className="px-2 ">
              <Button className="w-full text-white">تطبيق الفلتر</Button>
            </div>
          </SidebarFooter>
        </Sidebar> */}
        <main className="flex-1 w-full p-2 md:p-4 max-w-full overflow-x-hidden">
          {children}
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t bg-background py-4 text-center text-sm text-muted-foreground">
        <p>
          تم تطويره بواسطة [اسمك] لمادة تحليل الويب ومعالجة اللغة الطبيعية -
          ٢٠٢٥
        </p>
      </footer>
    </div>
  );
}
