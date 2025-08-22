import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  BusIcon as SoccerBall,
  BarChart3,
  FileText,
  Search,
} from "lucide-react";

export function AboutPage() {
  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between w-full">
        <h2 className="text-3xl font-bold tracking-tight">حول المشروع</h2>
      </div>

      <Card className="w-full">
        <CardHeader>
          <CardTitle>اتجاهات رياضية</CardTitle>
          <CardDescription>
            مشروع تحليل وعرض اتجاهات الرياضة في الوقت الفعلي
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p>
            يهدف هذا المشروع إلى تحليل وعرض اتجاهات الرياضة في الوقت الفعلي
            باستخدام تقنيات تحليل الويب ومعالجة اللغة الطبيعية.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6 w-full">
            <div className="flex flex-col items-center gap-2 p-6 bg-muted rounded-lg text-center">
              <SoccerBall className="h-12 w-12 text-primary" />
              <h3 className="text-xl font-bold">تحليل الرياضة</h3>
              <p className="text-muted-foreground">
                يقوم المشروع بتحليل المنشورات والتغريدات المتعلقة بالرياضة
                لاستخراج الاتجاهات والمواضيع الشائعة.
              </p>
            </div>
            <div className="flex flex-col items-center gap-2 p-6 bg-muted rounded-lg text-center">
              <BarChart3 className="h-12 w-12 text-primary" />
              <h3 className="text-xl font-bold">عرض البيانات</h3>
              <p className="text-muted-foreground">
                يوفر المشروع واجهة مستخدم سهلة الاستخدام لعرض البيانات
                والاتجاهات بطريقة مرئية وتفاعلية.
              </p>
            </div>
            <div className="flex flex-col items-center gap-2 p-6 bg-muted rounded-lg text-center">
              <FileText className="h-12 w-12 text-primary" />
              <h3 className="text-xl font-bold">إنشاء التقارير</h3>
              <p className="text-muted-foreground">
                يمكن للمستخدمين إنشاء تقارير مخصصة وتصديرها بتنسيقات مختلفة مثل
                PDF وCSV وPNG.
              </p>
            </div>
            <div className="flex flex-col items-center gap-2 p-6 bg-muted rounded-lg text-center">
              <Search className="h-12 w-12 text-primary" />
              <h3 className="text-xl font-bold">تحليل المشاعر</h3>
              <p className="text-muted-foreground">
                يقوم المشروع بتحليل مشاعر المستخدمين تجاه اللاعبين والفرق
                والأحداث الرياضية.
              </p>
            </div>
          </div>

          {/* <div className="mt-8 w-full">
            <h3 className="text-xl font-bold mb-4">التقنيات المستخدمة</h3>
            <ul className="list-disc list-inside space-y-2 mr-4">
              <li>React.js لبناء واجهة المستخدم التفاعلية</li>
              <li>Next.js كإطار عمل للتطبيق</li>
              <li>Tailwind CSS للتنسيق</li>
              <li>Recharts لإنشاء الرسوم البيانية</li>
              <li>معالجة اللغة الطبيعية لتحليل النصوص العربية</li>
              <li>تحليل المشاعر لتصنيف المنشورات</li>
            </ul>
          </div> */}

          <div className="mt-8 p-4 bg-primary/10 rounded-lg w-full">
            <h3 className="text-xl font-bold mb-2">فريق العمل</h3>
            <p className="mb-4">
              تم تطوير هذا المشروع كجزء من مادة تحليل الويب ومعالجة اللغة
              الطبيعية تحت إشراف رمزي بورامول.
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div className="p-3 bg-background rounded-lg text-center">
                <p className="font-semibold">زين الدين ربوح</p>
              </div>
              <div className="p-3 bg-background rounded-lg text-center">
                <p className="font-semibold">سعد عزام مندر</p>
              </div>
              <div className="p-3 bg-background rounded-lg text-center">
                <p className="font-semibold">يحي طولبية</p>
              </div>
              <div className="p-3 bg-background rounded-lg text-center">
                <p className="font-semibold">ياسين فردي</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
