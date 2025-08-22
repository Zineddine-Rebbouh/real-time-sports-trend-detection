"use client"

import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/components/ui/use-toast"
import { useAuth } from "@/hooks/use-auth"
import { DashboardLayout } from "@/components/dashboard-layout"
import { ProtectedRoute } from "@/components/protected-route"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

const profileSchema = z.object({
  name: z.string().min(2, { message: "الاسم يجب أن يكون حرفين على الأقل" }),
  email: z.string().email({ message: "يرجى إدخال بريد إلكتروني صحيح" }).optional(),
  bio: z.string().max(160, { message: "السيرة الذاتية يجب أن تكون أقل من 160 حرفًا" }).optional(),
})

export default function ProfilePage() {
  const { user } = useAuth()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)

  const form = useForm<z.infer<typeof profileSchema>>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: user?.name || "",
      email: user?.email || "",
      bio: "",
    },
  })

  async function onSubmit(values: z.infer<typeof profileSchema>) {
    setIsLoading(true)
    try {
      // In a real app, you would call your API to update the profile
      await new Promise((resolve) => setTimeout(resolve, 1000))

      toast({
        title: "تم تحديث الملف الشخصي",
        description: "تم تحديث معلومات ملفك الشخصي بنجاح.",
      })
    } catch (error) {
      toast({
        variant: "destructive",
        title: "فشل تحديث الملف الشخصي",
        description: "حدث خطأ أثناء تحديث معلومات ملفك الشخصي. يرجى المحاولة مرة أخرى.",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6 w-full dashboard-content">
          <div>
            <h3 className="text-lg font-medium">الملف الشخصي</h3>
            <p className="text-sm text-muted-foreground">هذه هي معلومات ملفك الشخصي التي ستظهر للآخرين.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 w-full">
            <Card>
              <CardHeader>
                <CardTitle>معلومات الملف الشخصي</CardTitle>
                <CardDescription>قم بتحديث معلومات ملفك الشخصي هنا.</CardDescription>
              </CardHeader>
              <CardContent>
                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>الاسم</FormLabel>
                          <FormControl>
                            <Input placeholder="محمد أحمد" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>البريد الإلكتروني</FormLabel>
                          <FormControl>
                            <Input placeholder="example@example.com" {...field} disabled />
                          </FormControl>
                          <FormDescription>لا يمكن تغيير البريد الإلكتروني.</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="bio"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>السيرة الذاتية</FormLabel>
                          <FormControl>
                            <Textarea placeholder="اكتب نبذة عنك هنا..." className="resize-none" {...field} />
                          </FormControl>
                          <FormDescription>يمكنك كتابة نبذة قصيرة عنك لتظهر في ملفك الشخصي.</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <Button type="submit" disabled={isLoading}>
                      {isLoading ? "جاري الحفظ..." : "حفظ التغييرات"}
                    </Button>
                  </form>
                </Form>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>الصورة الشخصية</CardTitle>
                <CardDescription>قم بتغيير صورتك الشخصية هنا.</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col items-center gap-4">
                <Avatar className="h-32 w-32">
                  <AvatarImage src={user?.image} alt={user?.name} />
                  <AvatarFallback className="text-4xl">{user?.name?.charAt(0) || "U"}</AvatarFallback>
                </Avatar>
                <div className="flex gap-2">
                  <Button variant="outline">تغيير الصورة</Button>
                  <Button variant="outline" className="text-destructive hover:text-destructive">
                    إزالة
                  </Button>
                </div>
              </CardContent>
              <CardFooter className="text-sm text-muted-foreground">
                يجب أن تكون الصورة بصيغة JPG أو PNG وبحجم أقل من 2 ميجابايت.
              </CardFooter>
            </Card>
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}

