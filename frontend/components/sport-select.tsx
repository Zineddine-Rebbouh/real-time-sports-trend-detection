"use client";

import { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { SportType } from "@/hooks/use-trends-data";

interface SportSelectProps {
  value: SportType;
  onValueChange: (value: SportType) => void;
}

export function SportSelect({ value, onValueChange }: SportSelectProps) {
  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="اختر الرياضة" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="كرة_القدم">كرة القدم</SelectItem>
        <SelectItem value="كرة_السلة">كرة السلة</SelectItem>
        <SelectItem value="تنس">تنس</SelectItem>
        <SelectItem value="ملاكمة">ملاكمة</SelectItem>
      </SelectContent>
    </Select>
  );
}
