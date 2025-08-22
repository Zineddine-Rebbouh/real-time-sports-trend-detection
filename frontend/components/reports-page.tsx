"use client";

import { useState, useRef } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DatePickerWithRange } from "@/components/date-range-picker";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Download, FileText, Image, FileDown, Loader2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { HashtagChart } from "@/components/charts/hashtag-chart";
import { exportAsImage, exportAsPDF, exportAsCSV } from "@/lib/utils";
import { toast } from "sonner";

interface ReportConfig {
  name: string;
  sport: string;
  entityType: string;
  entity: string;
  dateRange: { from: Date; to: Date } | undefined;
  chartType: string;
}

interface SavedReport extends ReportConfig {
  id: string;
  createdAt: string;
  data: any;
}

export function ReportsPage() {
  const [previewVisible, setPreviewVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const reportRef = useRef<HTMLDivElement>(null);
  const [reportConfig, setReportConfig] = useState<ReportConfig>({
    name: "",
    sport: "",
    entityType: "",
    entity: "",
    dateRange: undefined,
    chartType: "",
  });

  // Mock saved reports data
  const savedReports: SavedReport[] = Array.from({ length: 5 }).map((_, i) => ({
    id: `report-${i + 1}`,
    name: `تقرير شعبية الهاشتاغات ${i + 1}`,
    sport: "football",
    entityType: "hashtag",
    entity: "#الدوري_المصري",
    dateRange: undefined,
    chartType: ["line", "bar", "pie", "word-cloud", "sentiment"][i % 5],
    createdAt: `${i + 1}/5/2025`,
    data: {
      totalMentions: 35000,
      popularHashtag: "#الدوري_المصري",
      weeklyGrowth: "20%",
    },
  }));

  const handleExport = async (format: "pdf" | "png" | "csv") => {
    if (!reportRef.current) return;

    setLoading(true);
    try {
      switch (format) {
        case "pdf":
          await exportAsPDF(reportRef.current, reportConfig.name || "report");
          break;
        case "png":
          await exportAsImage(reportRef.current);
          break;
        case "csv":
          // For CSV export, we need to transform the chart data into a tabular format
          const data = [
            { date: "1/5/2025", mentions: 1200, hashtag: "#الدوري_المصري" },
            { date: "2/5/2025", mentions: 1900, hashtag: "#الدوري_المصري" },
            { date: "3/5/2025", mentions: 3000, hashtag: "#الدوري_المصري" },
          ];
          await exportAsCSV(data, reportConfig.name || "report");
          break;
      }
      toast.success("تم تصدير التقرير بنجاح");
    } catch (error) {
      console.error("Error exporting report:", error);
      toast.error("حدث خطأ أثناء تصدير التقرير");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReport = () => {
    // Validate required fields
    if (!reportConfig.name || !reportConfig.sport || !reportConfig.chartType) {
      toast.error("يرجى ملء جميع الحقول المطلوبة");
      return;
    }
    setPreviewVisible(true);
  };

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between w-full">
        <h2 className="text-3xl font-bold tracking-tight">التقارير</h2>
      </div>

      <Tabs defaultValue="create" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="create">إنشاء تقرير</TabsTrigger>
          <TabsTrigger value="saved">التقارير المحفوظة</TabsTrigger>
        </TabsList>
        <TabsContent value="create" className="space-y-4 pt-4 w-full">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>إنشاء تقرير جديد</CardTitle>
              <CardDescription>قم بتحديد معايير التقرير</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                <div className="space-y-2">
                  <Label htmlFor="report-name">اسم التقرير</Label>
                  <Input
                    id="report-name"
                    placeholder="أدخل اسم التقرير"
                    value={reportConfig.name}
                    onChange={(e) =>
                      setReportConfig((prev) => ({
                        ...prev,
                        name: e.target.value,
                      }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="sport">الرياضة</Label>
                  <Select
                    onValueChange={(value) =>
                      setReportConfig((prev) => ({ ...prev, sport: value }))
                    }
                  >
                    <SelectTrigger id="sport">
                      <SelectValue placeholder="اختر الرياضة" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="football">كرة القدم</SelectItem>
                      <SelectItem value="basketball">كرة السلة</SelectItem>
                      <SelectItem value="tennis">التنس</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="entity-type">نوع الكيان</Label>
                  <Select
                    onValueChange={(value) =>
                      setReportConfig((prev) => ({
                        ...prev,
                        entityType: value,
                      }))
                    }
                  >
                    <SelectTrigger id="entity-type">
                      <SelectValue placeholder="اختر نوع الكيان" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="player">لاعب</SelectItem>
                      <SelectItem value="team">فريق</SelectItem>
                      <SelectItem value="hashtag">هاشتاغ</SelectItem>
                      <SelectItem value="competition">مسابقة</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                {/* <div className="space-y-2">
                  <Label htmlFor="entity">الكيان</Label>
                  <Input
                    id="entity"
                    placeholder="أدخل اسم الكيان"
                    value={reportConfig.entity}
                    onChange={(e) =>
                      setReportConfig((prev) => ({
                        ...prev,
                        entity: e.target.value,
                      }))
                    }
                  />
                </div> */}
                <div className="space-y-2">
                  <Label>الفترة الزمنية</Label>
                  <DatePickerWithRange />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="chart-type">نوع الرسم البياني</Label>
                  <Select
                    onValueChange={(value) =>
                      setReportConfig((prev) => ({ ...prev, chartType: value }))
                    }
                  >
                    <SelectTrigger id="chart-type">
                      <SelectValue placeholder="اختر نوع الرسم البياني" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="line">خط بياني</SelectItem>
                      <SelectItem value="bar">رسم شريطي</SelectItem>
                      <SelectItem value="pie">رسم دائري</SelectItem>
                      <SelectItem value="word-cloud">سحابة كلمات</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button
                variant="outline"
                onClick={() =>
                  setReportConfig({
                    name: "",
                    sport: "",
                    entityType: "",
                    entity: "",
                    dateRange: undefined,
                    chartType: "",
                  })
                }
              >
                إعادة تعيين
              </Button>
              <Button onClick={handleCreateReport}>معاينة التقرير</Button>
            </CardFooter>
          </Card>

          {previewVisible && (
            <Card className="w-full">
              <CardHeader>
                <CardTitle>معاينة التقرير</CardTitle>
                <CardDescription>
                  {reportConfig.name || "تقرير شعبية الهاشتاغات في كرة القدم"}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4" ref={reportRef}>
                <HashtagChart />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 w-full">
                  <div className="bg-muted rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold">٣٥ ألف</div>
                    <div className="text-xs text-muted-foreground">
                      إجمالي المنشورات
                    </div>
                  </div>
                  <div className="bg-muted rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold">#الدوري_المصري</div>
                    <div className="text-xs text-muted-foreground">
                      أكثر هاشتاغ تداولًا
                    </div>
                  </div>
                  <div className="bg-muted rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold">٢٠٪</div>
                    <div className="text-xs text-muted-foreground">
                      زيادة أسبوعية
                    </div>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExport("pdf")}
                    disabled={loading}
                  >
                    <FileText className="ml-2 h-4 w-4" />
                    {loading ? "جاري التصدير..." : "تصدير PDF"}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExport("csv")}
                    disabled={loading}
                  >
                    <FileDown className="ml-2 h-4 w-4" />
                    {loading ? "جاري التصدير..." : "تصدير Excel"}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExport("png")}
                    disabled={loading}
                  >
                    <Image className="ml-2 h-4 w-4" />
                    {loading ? "جاري التصدير..." : "تصدير صورة"}
                  </Button>
                </div>
                <Button
                  onClick={() => {
                    // Here you would typically save the report to your backend
                    toast.success("تم حفظ التقرير بنجاح");
                  }}
                >
                  حفظ التقرير
                </Button>
              </CardFooter>
            </Card>
          )}
        </TabsContent>
        <TabsContent value="saved" className="pt-4 w-full">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>التقارير المحفوظة</CardTitle>
              <CardDescription>قائمة بالتقارير التي قمت بحفظها</CardDescription>
            </CardHeader>
            <CardContent className="w-full">
              <div className="w-full overflow-auto">
                <Table className="w-full">
                  <TableHeader>
                    <TableRow>
                      <TableHead>اسم التقرير</TableHead>
                      <TableHead>النوع</TableHead>
                      <TableHead>تاريخ الإنشاء</TableHead>
                      <TableHead>الإجراءات</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {savedReports.map((report) => (
                      <TableRow key={report.id}>
                        <TableCell className="font-medium">
                          {report.name}
                        </TableCell>
                        <TableCell>
                          {report.chartType === "line"
                            ? "خط بياني"
                            : report.chartType === "bar"
                            ? "رسم شريطي"
                            : report.chartType === "pie"
                            ? "رسم دائري"
                            : report.chartType === "word-cloud"
                            ? "سحابة كلمات"
                            : "تحليل مشاعر"}
                        </TableCell>
                        <TableCell>{report.createdAt}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleExport("pdf")}
                              disabled={loading}
                            >
                              <Download className="h-4 w-4" />
                              <span className="sr-only">تنزيل</span>
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => {
                                setReportConfig({
                                  ...report,
                                  dateRange: undefined, // Reset date range since it's not in the saved format
                                });
                                setPreviewVisible(true);
                              }}
                            >
                              <FileText className="h-4 w-4" />
                              <span className="sr-only">عرض</span>
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
