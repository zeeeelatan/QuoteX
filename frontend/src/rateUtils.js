// 维保费率与标准维保单价工具
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002';

// 获取所有费率
export async function fetchRates() {
  const res = await fetch(`${API_URL}/maintenance_rates/`);
  return await res.json();
}

// 根据分类查找费率（传入对象：{primary_category, secondary_category, tertiary_category}）
export function findRate(rates, {primary_category, secondary_category, tertiary_category}) {
  // 优先三级分类，依次降级
  let match = rates.find(r =>
    r.primary_category === primary_category &&
    r.secondary_category === secondary_category &&
    r.tertiary_category === tertiary_category
  );
  if (!match) {
    match = rates.find(r =>
      r.primary_category === primary_category &&
      r.secondary_category === secondary_category &&
      !r.tertiary_category
    );
  }
  if (!match) {
    match = rates.find(r =>
      r.primary_category === primary_category &&
      !r.secondary_category &&
      !r.tertiary_category
    );
  }
  return match ? Number(match.rate) : null;
}

// 计算标准维保单价
export function calcStandardRatePrice(devicePrice, rate) {
  if (!devicePrice || !rate) return null;
  // 费率已是小数（如0.06），直接参与计算
  return devicePrice * rate * 1.06;
}

// 计算三种不同的维保单价
export function calcMaintenancePrices(devicePrice, rate) {
  if (!devicePrice || !rate) return {
    untaxedPrice: null,
    price6Percent: null,
    price13Percent: null
  };
  
  const basePrice = devicePrice * rate; // 未税价格
  const price6Percent = basePrice * 1.06; // 含税6%价格
  const price13Percent = basePrice * 1.13; // 含税13%价格
  
  return {
    untaxedPrice: basePrice,
    price6Percent: price6Percent,
    price13Percent: price13Percent
  };
}
