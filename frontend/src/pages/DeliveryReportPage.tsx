import { Alert, Box, Button, CircularProgress, Dialog, DialogActions, DialogContent, DialogTitle, FormControlLabel, IconButton, InputAdornment, MenuItem, Paper, Radio, RadioGroup, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Tooltip, Typography } from "@mui/material";
import type { DeliveryReportPeriod, DeliverySettlementReport, } from "../models/DeliveryReport";
import { ResponseModal, type ResponseModalSeverity, } from "../components/ResponseModal";
import CleaningServicesOutlinedIcon from "@mui/icons-material/CleaningServicesOutlined";
import DeliveryDiningOutlinedIcon from "@mui/icons-material/DeliveryDiningOutlined";
import CalendarMonthOutlinedIcon from "@mui/icons-material/CalendarMonthOutlined";
import FileDownloadOutlinedIcon from "@mui/icons-material/FileDownloadOutlined";
import AssessmentOutlinedIcon from "@mui/icons-material/AssessmentOutlined";
import StorefrontOutlinedIcon from "@mui/icons-material/StorefrontOutlined";
import { deliveryReportService } from "../services/deliveryReportService";
import { absenceTypeService } from "../services/absenceTypeService";
import SearchOutlinedIcon from "@mui/icons-material/SearchOutlined";
import { domiciliaryService } from "../services/domiciliaryService";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { pointSaleService } from "../services/pointSaleService";
import { Fragment, useEffect, useMemo, useState } from "react";
import type { AbsenceType } from "../models/DeliveryRecord";
import { getErrorMessage } from "../services/errorService";
import type { Domiciliary } from "../models/Domiciliary";
import type { PointSale } from "../models/PointSale";
import { useAuth } from "../context/AuthContext";
import * as XLSX from "xlsx-js-style";

interface ResponseModalState {
  open: boolean;
  severity: ResponseModalSeverity;
  title: string;
  message: string;
}

const emptyResponseModal: ResponseModalState = {
  open: false,
  severity: "info",
  title: "",
  message: "",
};

interface ReportTotals {
  totalDeliveryQuantity: number;
  totalAbsences: number;
  totalValueSettlement: number;
  totalRecords: number;
}

interface DomiciliaryReportGroup extends ReportTotals {
  groupKey: string;
  IdDomiciliary: number;
  documentDomiciliary: string;
  nameDomiciliary: string;
  rows: DeliverySettlementReport[];
}

interface PointSaleReportGroup extends ReportTotals {
  groupKey: string;
  codePointSale: string;
  namePointSale: string;
  domiciliaryGroups: DomiciliaryReportGroup[];
}

type EditRecordMode = "delivery" | "absence";

const getToday = () => {
  const date = new Date();
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
  return date.toISOString().slice(0, 10);
};

const getFirstDayOfCurrentMonth = () => {
  const date = new Date();
  const firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
  firstDay.setMinutes(firstDay.getMinutes() - firstDay.getTimezoneOffset());
  return firstDay.toISOString().slice(0, 10);
};

export function DeliveryReportPage() {
  const [responseModal, setResponseModal] = useState<ResponseModalState>(emptyResponseModal);
  const [editingRow, setEditingRow] = useState<DeliverySettlementReport | null>(null);
  const [editRecordMode, setEditRecordMode] = useState<EditRecordMode>("delivery");
  const [selectedDomiciliaryId, setSelectedDomiciliaryId] = useState<number>(0);
  const [reportData, setReportData] = useState<DeliverySettlementReport[]>([]);
  const [editingAbsenceTypeId, setEditingAbsenceTypeId] = useState<number>(0);
  const [selectedPointSaleId, setSelectedPointSaleId] = useState<number>(0);  
  const [startDate, setStartDate] = useState(getFirstDayOfCurrentMonth());
  const [loadingDomiciliaries, setLoadingDomiciliaries] = useState(false);
  const [loadingAbsenceTypes, setLoadingAbsenceTypes] = useState(false);
  const [domiciliaries, setDomiciliaries] = useState<Domiciliary[]>([]);
  const [absenceTypes, setAbsenceTypes] = useState<AbsenceType[]>([]);
  const [editValidationError, setEditValidationError] = useState("");
  const [loadingPointSales, setLoadingPointSales] = useState(false);
  const [period, setPeriod] = useState<DeliveryReportPeriod>("day");
  const [pointSales, setPointSales] = useState<PointSale[]>([]);
  const [savingQuantity, setSavingQuantity] = useState(false);
  const [validationError, setValidationError] = useState("");
  const [editingQuantity, setEditingQuantity] = useState("");
  const [loadingReport, setLoadingReport] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [endDate, setEndDate] = useState(getToday());
  const { user } = useAuth();
  const normalizeRole = (value: string) =>
    value
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim()
      .toLowerCase();
  const canUpdateDeliveryQuantity =
    user?.roles?.some((role) =>
      ["operaciones", "administrador"].includes(normalizeRole(role.nameRole))
    ) ?? false;

  console.log("[QA REPORT] user:", user);
  console.log("[QA REPORT] roles:", user?.roles);
  console.log("[QA REPORT] roles normalizados:", user?.roles?.map((role) => normalizeRole(role.nameRole)));
  console.log("[QA REPORT] puede editar:", canUpdateDeliveryQuantity);

  const showResponseModal = (severity: ResponseModalSeverity, title: string, message: string) => {
    setResponseModal({
      open: true,
      severity,
      title,
      message,
    });
  };

  const closeResponseModal = () => {
    setResponseModal((prev) => ({
      ...prev,
      open: false,
    }));
  };

  const formatCurrency = (value: number | string) => {
    const numericValue = Number(value);

    if (Number.isNaN(numericValue)) {
      return "$0";
    }

    return numericValue.toLocaleString("es-CO", {
      style: "currency",
      currency: "COP",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });
  };

  const getPeriodLabel = (value: DeliveryReportPeriod) => {
    if (value === "day") return "Día";
    if (value === "week") return "Semana";
    return "Mes";
  };

  const getAbsenceNames = (absenceTypes?: string | null) => {
    return (absenceTypes ?? "")
      .split(",")
      .map((item) => item.trim())
      .filter((item) => item.length > 0);
  };

  const getAbsenceSummaryFromNames = (names: string[]) => {
    if (names.length === 0) {
      return "Sin ausentismo";
    }

    const counter = names.reduce<Record<string, number>>((acc, name) => {
      acc[name] = (acc[name] ?? 0) + 1;
      return acc;
    }, {});

    return Object.entries(counter)
      .map(([name, count]) => (count > 1 ? `${name} (${count})` : name))
      .join(", ");
  };

  const getAbsenceSummary = (absenceTypes?: string | null) => {
    return getAbsenceSummaryFromNames(getAbsenceNames(absenceTypes));
  };

  const loadAbsenceTypes = async () => {
    try {
      setLoadingAbsenceTypes(true);
      const response = await absenceTypeService.getAll();
      setAbsenceTypes((response.result ?? []).filter((item) => item.statusAbsenceType));
    } catch (err) {
      setAbsenceTypes([]);
      showResponseModal("error", "Error al cargar ausentismos", getErrorMessage(err));
    } finally {
      setLoadingAbsenceTypes(false);
    }
  };
  
  const totals = useMemo<ReportTotals>(() => {
    return reportData.reduce(
      (acc, item) => {
        acc.totalDeliveryQuantity += Number(item.totalDeliveryQuantity ?? 0);
        acc.totalAbsences += Number(item.totalAbsences ?? 0);
        acc.totalValueSettlement += Number(item.totalValueSettlement ?? 0);
        acc.totalRecords += Number(item.totalRecords ?? 0);
        return acc;
      },
      {
        totalDeliveryQuantity: 0,
        totalAbsences: 0,
        totalValueSettlement: 0,
        totalRecords: 0,
      }
    );
  }, [reportData]);

  const parameterColumnName = reportData.find((item) => item.parameterNameSettlement) ?.parameterNameSettlement ?? "Parámetro";

  const groupedReportData = useMemo<PointSaleReportGroup[]>(() => {
    const sortedData = [...reportData].sort((a, b) => {
      const pointSaleCompare = `${a.namePointSale} ${a.codePointSale}`.localeCompare(
        `${b.namePointSale} ${b.codePointSale}`
      );

      if (pointSaleCompare !== 0) return pointSaleCompare;

      const domiciliaryCompare = `${a.nameDomiciliary} ${a.documentDomiciliary}`.localeCompare(
        `${b.nameDomiciliary} ${b.documentDomiciliary}`
      );

      if (domiciliaryCompare !== 0) return domiciliaryCompare;

      return a.periodKey.localeCompare(b.periodKey);
    });

    const pointSaleGroups: PointSaleReportGroup[] = [];

    sortedData.forEach((item) => {
      const pointSaleGroupKey = String(item.IdPointSale);

      let pointSaleGroup = pointSaleGroups.find(
        (current) => current.groupKey === pointSaleGroupKey
      );

      if (!pointSaleGroup) {
        pointSaleGroup = {
          groupKey: pointSaleGroupKey,
          codePointSale: item.codePointSale,
          namePointSale: item.namePointSale,
          domiciliaryGroups: [],
          totalDeliveryQuantity: 0,
          totalAbsences: 0,
          totalValueSettlement: 0,
          totalRecords: 0,
        };

        pointSaleGroups.push(pointSaleGroup);
      }

      const domiciliaryGroupKey = String(item.IdDomiciliary);

      let domiciliaryGroup = pointSaleGroup.domiciliaryGroups.find(
        (current) => current.groupKey === domiciliaryGroupKey
      );

      if (!domiciliaryGroup) {
        domiciliaryGroup = {
          groupKey: domiciliaryGroupKey,
          IdDomiciliary: item.IdDomiciliary,
          documentDomiciliary: item.documentDomiciliary,
          nameDomiciliary: item.nameDomiciliary,
          rows: [],
          totalDeliveryQuantity: 0,
          totalAbsences: 0,
          totalValueSettlement: 0,
          totalRecords: 0,
        };

        pointSaleGroup.domiciliaryGroups.push(domiciliaryGroup);
      }

      domiciliaryGroup.rows.push(item);

      domiciliaryGroup.totalDeliveryQuantity += Number(item.totalDeliveryQuantity ?? 0);
      domiciliaryGroup.totalAbsences += Number(item.totalAbsences ?? 0);
      domiciliaryGroup.totalValueSettlement += Number(item.totalValueSettlement ?? 0);
      domiciliaryGroup.totalRecords += Number(item.totalRecords ?? 0);

      pointSaleGroup.totalDeliveryQuantity += Number(item.totalDeliveryQuantity ?? 0);
      pointSaleGroup.totalAbsences += Number(item.totalAbsences ?? 0);
      pointSaleGroup.totalValueSettlement += Number(item.totalValueSettlement ?? 0);
      pointSaleGroup.totalRecords += Number(item.totalRecords ?? 0);
    });

    return pointSaleGroups;
  }, [reportData]);

  const loadPointSales = async () => {
    try {
      setLoadingPointSales(true);
      const response = await pointSaleService.getAll();
      setPointSales((response.result ?? []).filter((item) => item.statusPointSale));
    } catch (err) {
      setPointSales([]);
      showResponseModal(
        "error",
        "Error al cargar puntos de venta",
        getErrorMessage(err)
      );
    } finally {
      setLoadingPointSales(false);
    }
  };

  const loadDomiciliariesByPointSale = async (idPointSale: number) => {
    try {
      setDomiciliaries([]);
      setSelectedDomiciliaryId(0);

      if (!idPointSale || idPointSale <= 0) {
        return;
      }

      setLoadingDomiciliaries(true);

      const response = await domiciliaryService.getAll({
        pointSale: idPointSale,
        statusDomiciliary: true,
      });

      setDomiciliaries(response.result ?? []);
    } catch (err) {
      setDomiciliaries([]);
      showResponseModal(
        "error",
        "Error al cargar domiciliarios",
        getErrorMessage(err)
      );
    } finally {
      setLoadingDomiciliaries(false);
    }
  };

  const handleChangePointSale = (idPointSale: number) => {
    setSelectedPointSaleId(idPointSale);
    setSelectedDomiciliaryId(0);
    loadDomiciliariesByPointSale(idPointSale);
  };

  const validateFilters = () => {
    if (!startDate) {
      return "La fecha inicial es obligatoria.";
    }

    if (!endDate) {
      return "La fecha final es obligatoria.";
    }

    if (endDate < startDate) {
      return "La fecha final no puede ser menor que la fecha inicial.";
    }

    if (!period) {
      return "Debes seleccionar un periodo.";
    }

    return "";
  };

  const handleSearchReport = async () => {
    try {
      const error = validateFilters();

      if (error) {
        setValidationError(error);
        return;
      }

      setLoadingReport(true);
      setValidationError("");

      const response = await deliveryReportService.getSettlementReport({
        startDate,
        endDate,
        period,
        IdPointSale: selectedPointSaleId > 0 ? selectedPointSaleId : undefined,
        IdDomiciliary: selectedDomiciliaryId > 0 ? selectedDomiciliaryId : undefined,
      });

      setReportData(response.result ?? []);

      if (!response.isSuccess || (response.result ?? []).length === 0) {
        showResponseModal(
          "info",
          "Sin resultados",
          response.Message ||
            "No existen datos para el reporte con los filtros enviados."
        );
      }
    } catch (err) {
      setReportData([]);
      showResponseModal(
        "error",
        "Error al consultar reporte",
        getErrorMessage(err)
      );
    } finally {
      setLoadingReport(false);
    }
  };

  const handleClearFilters = () => {
    setStartDate(getFirstDayOfCurrentMonth());
    setEndDate(getToday());
    setPeriod("day");
    setSelectedPointSaleId(0);
    setSelectedDomiciliaryId(0);
    setDomiciliaries([]);
    setReportData([]);
    setValidationError("");
  };

  const handleOpenEditModal = (item: DeliverySettlementReport) => {
    if (period !== "day") {
      showResponseModal(
        "warning",
        "Edición no disponible",
        "Para editar la cantidad de domicilios debes consultar el reporte por día."
      );
      return;
    }

    if (!item.IdDeliveryRecord) {
      showResponseModal(
        "warning",
        "No se puede editar",
        "Este registro no tiene identificador de domicilio. Revisa que el backend esté devolviendo IdDeliveryRecord."
      );
      return;
    }

    if (Number(item.totalRecords ?? 0) !== 1) {
      showResponseModal(
        "warning",
        "No se puede editar",
        "Este resultado agrupa más de un registro. Filtra el reporte por día para editar un registro puntual."
      );
      return;
    }

    const absenceName = getAbsenceNames(item.absenceTypes)[0] ?? "";

    const matchedAbsenceType = absenceTypes.find(
      (absenceType) =>
        normalizeRole(absenceType.nameAbsenceType) === normalizeRole(absenceName)
    );

    const hasAbsence = Number(item.totalAbsences ?? 0) > 0 || absenceName.length > 0;

    setEditingRow(item);
    setEditRecordMode(hasAbsence ? "absence" : "delivery");
    setEditingQuantity(hasAbsence ? "" : String(Number(item.totalDeliveryQuantity ?? 0)));
    setEditingAbsenceTypeId(matchedAbsenceType?.IdAbsenceType ?? 0);
    setEditValidationError("");
    setEditModalOpen(true);
  };

  const handleCloseEditModal = () => {
    if (savingQuantity) return;

    setEditModalOpen(false);
    setEditingRow(null);
    setEditingQuantity("");
    setEditingAbsenceTypeId(0);
    setEditRecordMode("delivery");
    setEditValidationError("");
  };

  const handleSaveQuantity = async () => {
    try {
      if (!editingRow?.IdDeliveryRecord) {
        setEditValidationError("No se encontró el identificador del registro.");
        return;
      }

      let payload: {
        deliveryQuantity?: number;
        IdAbsenceType?: number | null;
      } = {};

      if (editRecordMode === "delivery") {
        const quantity = Number(editingQuantity);

        if (!Number.isInteger(quantity)) {
          setEditValidationError("La cantidad debe ser un número entero.");
          return;
        }

        if (quantity <= 0) {
          setEditValidationError("La cantidad de domicilios debe ser mayor a cero.");
          return;
        }

        payload = {
          deliveryQuantity: quantity,
          IdAbsenceType: null,
        };
      }

      if (editRecordMode === "absence") {
        if (!editingAbsenceTypeId || editingAbsenceTypeId <= 0) {
          setEditValidationError("Debes seleccionar un tipo de ausentismo.");
          return;
        }

        payload = {
          IdAbsenceType: editingAbsenceTypeId,
        };
      }

      setSavingQuantity(true);
      setEditValidationError("");

      const response = await deliveryReportService.updateDeliveryQuantityFromReport(
        editingRow.IdDeliveryRecord,
        payload
      );

      if (!response.isSuccess || !response.result) {
        showResponseModal("warning", "No se pudo actualizar", response.Message || "No fue posible actualizar el registro.");
        return;
      }

      showResponseModal("success", "Registro actualizado", response.Message || "El registro fue actualizado correctamente.");

      setEditModalOpen(false);
      setEditingRow(null);
      setEditingQuantity("");
      setEditingAbsenceTypeId(0);
      setEditRecordMode("delivery");

      await handleSearchReport();
    } catch (err) {
      showResponseModal("error", "Error al actualizar", getErrorMessage(err));
    } finally {
      setSavingQuantity(false);
    }
  };

  const handleExportReport = () => {
    if (reportData.length === 0) {
      showResponseModal("warning", "Sin datos para exportar", "Primero debes consultar el reporte antes de exportarlo.");
      return;
    }

    const columns = [
      "Periodo",
      "Punto de venta",
      "Domiciliario",
      "Documento",
      "Registrado por",
      parameterColumnName,
      "Domicilios",
      "Ausentismo",
      "Cant. ausentismos",
      "Valor total",
      "Registros",
    ];

    const rows: (string | number)[][] = [];

    rows.push(["REPORTE DE DOMICILIOS"]);
    rows.push([`Fecha de generación: ${new Date().toLocaleString("es-CO")}`]);
    rows.push([`Filtros: ${startDate} a ${endDate} | Periodo: ${getPeriodLabel(period)}`,]);
    rows.push([]);
    rows.push(columns);

    const groupHeaderRows: number[] = [];
    const subtotalRows: number[] = [];

    groupedReportData.forEach((pointSaleGroup) => {
      groupHeaderRows.push(rows.length);
      rows.push([`Punto de venta: ${pointSaleGroup.codePointSale} - ${pointSaleGroup.namePointSale}`]);

      pointSaleGroup.domiciliaryGroups.forEach((domiciliaryGroup) => {
        groupHeaderRows.push(rows.length);
        rows.push([`Domiciliario: ${domiciliaryGroup.nameDomiciliary} - ${domiciliaryGroup.documentDomiciliary}`]);

        domiciliaryGroup.rows.forEach((item) => {
          rows.push([
            item.periodLabel,
            `${item.codePointSale} - ${item.namePointSale}`,
            item.nameDomiciliary,
            item.documentDomiciliary,
            item.createdByUsers || "Sin información",
            Number(item.parameterValueSettlement ?? 0),
            Number(item.totalDeliveryQuantity ?? 0),
            getAbsenceSummary(item.absenceTypes),
            Number(item.totalAbsences ?? 0),
            Number(item.totalValueSettlement ?? 0),
            Number(item.totalRecords ?? 0),
          ]);
        });

        subtotalRows.push(rows.length);

        rows.push([
          "",
          "",
          `Subtotal domiciliario: ${domiciliaryGroup.nameDomiciliary}`,
          domiciliaryGroup.documentDomiciliary,
          "",
          "",
          domiciliaryGroup.totalDeliveryQuantity,
          "",
          domiciliaryGroup.totalAbsences,
          domiciliaryGroup.totalValueSettlement,
          domiciliaryGroup.totalRecords,
        ]);
      });

      subtotalRows.push(rows.length);

      rows.push([
        "",
        `Subtotal punto de venta: ${pointSaleGroup.codePointSale} - ${pointSaleGroup.namePointSale}`,
        "",
        "",
        "",
        "",
        pointSaleGroup.totalDeliveryQuantity,
        "",
        pointSaleGroup.totalAbsences,
        pointSaleGroup.totalValueSettlement,
        pointSaleGroup.totalRecords,
      ]);

      rows.push([]);
    });

    const totalRowIndex = rows.length;

    rows.push([
      "",
      "",
      "TOTAL GENERAL",
      "",
      "",
      "",
      totals.totalDeliveryQuantity,
      "",
      totals.totalAbsences,
      totals.totalValueSettlement,
      totals.totalRecords,
    ]);

    const worksheet = XLSX.utils.aoa_to_sheet(rows);
    const workbook = XLSX.utils.book_new();

    worksheet["!cols"] = [
      { wch: 16 },
      { wch: 32 },
      { wch: 34 },
      { wch: 16 },
      { wch: 24 },
      { wch: 16 },
      { wch: 12 },
      { wch: 32 },
      { wch: 18 },
      { wch: 18 },
      { wch: 12 },
    ];

    worksheet["!rows"] = rows.map((_, index) => {
      if (index === 0) return { hpt: 28 };
      if (index === 4) return { hpt: 24 };
      return { hpt: 20 };
    });

    worksheet["!merges"] = [
      { s: { r: 0, c: 0 }, e: { r: 0, c: columns.length - 1 } },
      { s: { r: 1, c: 0 }, e: { r: 1, c: columns.length - 1 } },
      { s: { r: 2, c: 0 }, e: { r: 2, c: columns.length - 1 } },
      ...groupHeaderRows.map((rowIndex) => ({
        s: { r: rowIndex, c: 0 },
        e: { r: rowIndex, c: columns.length - 1 },
      })),
    ];

    worksheet["!autofilter"] = {
      ref: `A5:K5`,
    };

    const titleStyle = {
      font: { bold: true, sz: 16, color: { rgb: "FFFFFF" } },
      fill: { patternType: "solid", fgColor: { rgb: "4B2E1F" } },
      alignment: { horizontal: "center", vertical: "center" },
    };

    const subtitleStyle = {
      font: { bold: true, sz: 11, color: { rgb: "4B2E1F" } },
      fill: { patternType: "solid", fgColor: { rgb: "F7E8D8" } },
      alignment: { horizontal: "center", vertical: "center" },
    };

    const headerStyle = {
      font: { bold: true, color: { rgb: "4B2E1F" } },
      fill: { patternType: "solid", fgColor: { rgb: "F7E8D8" } },
      alignment: { horizontal: "center", vertical: "center", wrapText: true },
      border: {
        top: { style: "thin", color: { rgb: "C9A98E" } },
        bottom: { style: "thin", color: { rgb: "C9A98E" } },
        left: { style: "thin", color: { rgb: "C9A98E" } },
        right: { style: "thin", color: { rgb: "C9A98E" } },
      },
    };

    const groupStyle = {
      font: { bold: true, color: { rgb: "4B2E1F" } },
      fill: { patternType: "solid", fgColor: { rgb: "FFF8EF" } },
      alignment: { horizontal: "left", vertical: "center" },
      border: {
        top: { style: "thin", color: { rgb: "E0CDBB" } },
        bottom: { style: "thin", color: { rgb: "E0CDBB" } },
      },
    };

    const subtotalStyle = {
      font: { bold: true, color: { rgb: "4B2E1F" } },
      fill: { patternType: "solid", fgColor: { rgb: "F7E8D8" } },
      border: {
        top: { style: "thin", color: { rgb: "C9A98E" } },
        bottom: { style: "thin", color: { rgb: "C9A98E" } },
      },
    };

    const totalStyle = {
      font: { bold: true, color: { rgb: "FFFFFF" } },
      fill: { patternType: "solid", fgColor: { rgb: "4B2E1F" } },
      border: {
        top: { style: "thin", color: { rgb: "4B2E1F" } },
        bottom: { style: "thin", color: { rgb: "4B2E1F" } },
      },
    };

    const normalStyle = {
      border: {
        top: { style: "thin", color: { rgb: "E8D8C8" } },
        bottom: { style: "thin", color: { rgb: "E8D8C8" } },
        left: { style: "thin", color: { rgb: "F0E4D8" } },
        right: { style: "thin", color: { rgb: "F0E4D8" } },
      },
      alignment: { vertical: "center", wrapText: true },
    };

    const numberStyle = {
      ...normalStyle,
      alignment: { horizontal: "right", vertical: "center" },
    };

    const currencyStyle = {
      ...numberStyle,
      numFmt: '"$"#,##0',
    };

    const getCell = (rowIndex: number, columnIndex: number) => {
      const cellRef = XLSX.utils.encode_cell({
        r: rowIndex,
        c: columnIndex,
      });

      if (!worksheet[cellRef]) {
        worksheet[cellRef] = { t: "s", v: "" };
      }

      return worksheet[cellRef] as any;
    };

    const applyStyleToRow = (rowIndex: number, style: any) => {
      for (let columnIndex = 0; columnIndex < columns.length; columnIndex++) {
        getCell(rowIndex, columnIndex).s = style;
      }
    };

    applyStyleToRow(0, titleStyle);
    applyStyleToRow(1, subtitleStyle);
    applyStyleToRow(2, subtitleStyle);
    applyStyleToRow(4, headerStyle);

    groupHeaderRows.forEach((rowIndex) => {
      applyStyleToRow(rowIndex, groupStyle);
    });

    subtotalRows.forEach((rowIndex) => {
      applyStyleToRow(rowIndex, subtotalStyle);
    });

    applyStyleToRow(totalRowIndex, totalStyle);

    const range = XLSX.utils.decode_range(worksheet["!ref"] ?? "A1:J1");

    for (let rowIndex = 5; rowIndex <= range.e.r; rowIndex++) {
      if (
        groupHeaderRows.includes(rowIndex) ||
        subtotalRows.includes(rowIndex) ||
        rowIndex === totalRowIndex
      ) {
        continue;
      }

      for (let columnIndex = 0; columnIndex < columns.length; columnIndex++) {
        const cell = getCell(rowIndex, columnIndex);

        if (columnIndex === 5 || columnIndex === 8) {
          cell.s = currencyStyle;
        } else if ([6, 7, 9].includes(columnIndex)) {
          cell.s = numberStyle;
        } else {
          cell.s = normalStyle;
        }
      }
    }

    subtotalRows.forEach((rowIndex) => {
      getCell(rowIndex, 5).s = currencyStyle;
      getCell(rowIndex, 6).s = subtotalStyle;
      getCell(rowIndex, 7).s = subtotalStyle;
      getCell(rowIndex, 8).s = {
        ...subtotalStyle,
        numFmt: '"$"#,##0',
        alignment: { horizontal: "right", vertical: "center" },
      };
      getCell(rowIndex, 9).s = subtotalStyle;
    });

    getCell(totalRowIndex, 5).s = totalStyle;
    getCell(totalRowIndex, 6).s = totalStyle;
    getCell(totalRowIndex, 7).s = totalStyle;
    getCell(totalRowIndex, 8).s = {
      ...totalStyle,
      numFmt: '"$"#,##0',
      alignment: { horizontal: "right", vertical: "center" },
    };
    getCell(totalRowIndex, 9).s = totalStyle;

    XLSX.utils.book_append_sheet(workbook, worksheet, "Reporte domicilios");

    const fileName = `reporte_domicilios_${startDate}_${endDate}_${period}.xlsx`;

    XLSX.writeFile(workbook, fileName);
  };

  useEffect(() => {
    loadPointSales();
    loadAbsenceTypes();
  }, []);

  return (
    <Stack spacing={3}>
      <Stack
        sx={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Stack
          sx={{
            display: "flex",
            flexDirection: "row",
            gap: 1.5,
            alignItems: "center",
          }}
        >
          <AssessmentOutlinedIcon sx={{ color: "#4B2E1F", fontSize: 30 }} />

          <Typography
            sx={{
              color: "#4B2E1F",
              fontSize: 26,
              fontWeight: 700,
            }}
          >
            Reporte de domicilios
          </Typography>
        </Stack>

        <Button
          variant="outlined"
          startIcon={<FileDownloadOutlinedIcon />}
          onClick={handleExportReport}
          disabled={loadingReport || reportData.length === 0}
          sx={{
            borderColor: "#8B6A55",
            color: "#4B2E1F",
            textTransform: "none",
            fontWeight: 600,
            "&:hover": {
              borderColor: "#4B2E1F",
              bgcolor: "rgba(75, 46, 31, 0.05)",
            },
          }}
        >
          Exportar
        </Button>
      </Stack>

      <Paper
        elevation={0}
        sx={{
          border: "1px solid #E0CDBB",
          borderRadius: 2,
          p: 3,
        }}
      >
        <Stack spacing={2.5}>
          <Typography
            sx={{
              color: "#4B2E1F",
              fontSize: 18,
              fontWeight: 700,
            }}
          >
            Filtros del reporte
          </Typography>

          {validationError && (
            <Alert severity="warning">{validationError}</Alert>
          )}

          <Stack
            sx={{
              display: "grid",
              gridTemplateColumns: {
                xs: "1fr",
                md: "repeat(3, minmax(0, 1fr))",
              },
              gap: 2,
            }}
          >
            <TextField
              label="Fecha inicial"
              type="date"
              value={startDate}
              disabled={loadingReport}
              fullWidth
              onChange={(event) => setStartDate(event.target.value)}
              slotProps={{
                inputLabel: {
                  shrink: true,
                },
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <CalendarMonthOutlinedIcon sx={{ color: "#8B6A55" }} />
                    </InputAdornment>
                  ),
                },
              }}
            />

            <TextField
              label="Fecha final"
              type="date"
              value={endDate}
              disabled={loadingReport}
              fullWidth
              onChange={(event) => setEndDate(event.target.value)}
              slotProps={{
                inputLabel: {
                  shrink: true,
                },
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <CalendarMonthOutlinedIcon sx={{ color: "#8B6A55" }} />
                    </InputAdornment>
                  ),
                },
              }}
            />

            <TextField
              select
              label="Periodo"
              value={period}
              disabled={loadingReport}
              fullWidth
              onChange={(event) =>
                setPeriod(event.target.value as DeliveryReportPeriod)
              }
            >
              <MenuItem value="day">Día</MenuItem>
              <MenuItem value="week">Semana</MenuItem>
              <MenuItem value="month">Mes</MenuItem>
            </TextField>

            <TextField
              select
              label="Punto de venta"
              value={selectedPointSaleId}
              disabled={loadingReport || loadingPointSales}
              fullWidth
              onChange={(event) =>
                handleChangePointSale(Number(event.target.value))
              }
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <StorefrontOutlinedIcon sx={{ color: "#8B6A55" }} />
                    </InputAdornment>
                  ),
                },
              }}
            >
              <MenuItem value={0}>Todos los puntos de venta</MenuItem>

              {pointSales.map((item) => (
                <MenuItem key={item.IdPointSale} value={item.IdPointSale}>
                  {item.codePointSale} - {item.namePointSale}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              select
              label="Domiciliario"
              value={selectedDomiciliaryId}
              disabled={
                loadingReport ||
                loadingDomiciliaries ||
                selectedPointSaleId === 0
              }
              fullWidth
              onChange={(event) =>
                setSelectedDomiciliaryId(Number(event.target.value))
              }
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <DeliveryDiningOutlinedIcon sx={{ color: "#8B6A55" }} />
                    </InputAdornment>
                  ),
                },
              }}
            >
              <MenuItem value={0}>
                {selectedPointSaleId === 0
                  ? "Selecciona primero un punto de venta"
                  : "Todos los domiciliarios"}
              </MenuItem>

              {domiciliaries.map((item) => (
                <MenuItem key={item.IdDomiciliary} value={item.IdDomiciliary}>
                  {item.documentDomiciliary} - {item.nameDomiciliary}
                </MenuItem>
              ))}
            </TextField>

            <Stack
              sx={{
                display: "flex",
                flexDirection: "row",
                gap: 1,
              }}
            >
              <Button
                variant="outlined"
                onClick={handleClearFilters}
                disabled={loadingReport}
                sx={{
                  minWidth: 56,
                  width: 56,
                  height: 56,
                  borderColor: "#8B6A55",
                  color: "#4B2E1F",
                  p: 0,
                  "&:hover": {
                    borderColor: "#4B2E1F",
                    bgcolor: "rgba(75, 46, 31, 0.05)",
                  },
                }}
              >
                <CleaningServicesOutlinedIcon />
              </Button>

              <Button
                variant="contained"
                startIcon={
                  loadingReport ? (
                    <CircularProgress size={16} sx={{ color: "#FFFFFF" }} />
                  ) : (
                    <SearchOutlinedIcon />
                  )
                }
                onClick={handleSearchReport}
                disabled={loadingReport}
                fullWidth
                sx={{
                  height: 56,
                  bgcolor: "#4B2E1F",
                  color: "#FFFFFF",
                  textTransform: "none",
                  fontWeight: 600,
                  "&:hover": {
                    bgcolor: "#3A2318",
                  },
                }}
              >
                {loadingReport ? "Consultando..." : "Consultar"}
              </Button>
            </Stack>
          </Stack>
        </Stack>
      </Paper>

      {reportData.length > 0 && (
        <Stack
          sx={{
            display: "grid",
            gridTemplateColumns: {
              xs: "1fr",
              md: "repeat(4, minmax(0, 1fr))",
            },
            gap: 2,
          }}
        >
          <Paper elevation={0} sx={{ border: "1px solid #E0CDBB", borderRadius: 2, p: 2 }}>
            <Typography sx={{ color: "#6B4A3A", fontSize: 13 }}>
              Total domicilios
            </Typography>
            <Typography sx={{ color: "#4B2E1F", fontSize: 26, fontWeight: 800 }}>
              {totals.totalDeliveryQuantity}
            </Typography>
          </Paper>

          <Paper elevation={0} sx={{ border: "1px solid #E0CDBB", borderRadius: 2, p: 2 }}>
            <Typography sx={{ color: "#6B4A3A", fontSize: 13 }}>
              Total ausentismos 
            </Typography>
            <Typography sx={{ color: "#4B2E1F", fontSize: 26, fontWeight: 800 }}>
              {totals.totalAbsences}
            </Typography>
          </Paper>

          <Paper elevation={0} sx={{ border: "1px solid #E0CDBB", borderRadius: 2, p: 2 }}>
            <Typography sx={{ color: "#6B4A3A", fontSize: 13 }}>
              Valor total
            </Typography>
            <Typography sx={{ color: "#4B2E1F", fontSize: 26, fontWeight: 800 }}>
              {formatCurrency(totals.totalValueSettlement)}
            </Typography>
          </Paper>

          <Paper elevation={0} sx={{ border: "1px solid #E0CDBB", borderRadius: 2, p: 2 }}>
            <Typography sx={{ color: "#6B4A3A", fontSize: 13 }}>
              Registros
            </Typography>
            <Typography sx={{ color: "#4B2E1F", fontSize: 26, fontWeight: 800 }}>
              {totals.totalRecords}
            </Typography>
          </Paper>
        </Stack>
      )}

      <Paper
        elevation={0}
        sx={{
          border: "1px solid #E0CDBB",
          borderRadius: 2,
          overflow: "hidden",
        }}
      >
        {loadingReport ? (
          <Box sx={{ py: 6, display: "flex", justifyContent: "center" }}>
            <CircularProgress sx={{ color: "#4B2E1F" }} />
          </Box>
        ) : (
          <Box sx={{ width: "100%", overflowX: "auto", overflowY: "hidden", WebkitOverflowScrolling: "touch", }}>
            <Table sx={{ minWidth: 1500, tableLayout: "auto", "& .MuiTableCell-root": { whiteSpace: "nowrap", }, }}>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>Periodo</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>Punto de venta</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>Domiciliario</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>Documento</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>Registrado por</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, color: "#4B2E1F" }}> {parameterColumnName} </TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, color: "#4B2E1F" }}>Domicilios</TableCell>
                  <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>Ausentismo</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, color: "#4B2E1F" }}>Cant. ausentismos</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, color: "#4B2E1F" }}>Valor total</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, color: "#4B2E1F" }}>Registros</TableCell>
                  {canUpdateDeliveryQuantity && ( <TableCell align="center" sx={{ fontWeight: 700, color: "#4B2E1F" }}>Acciones</TableCell> )}
                </TableRow>
              </TableHead>

              <TableBody>
                {groupedReportData.map((pointSaleGroup) => (
                  <Fragment key={pointSaleGroup.groupKey}>
                    <TableRow>
                      <TableCell colSpan={12} sx={{ fontWeight: 800, color: "#4B2E1F", bgcolor: "#FFF8EF" }}>
                        Punto de venta: {pointSaleGroup.codePointSale} - {pointSaleGroup.namePointSale}
                      </TableCell>
                    </TableRow>

                    {pointSaleGroup.domiciliaryGroups.map((domiciliaryGroup) => (
                      <Fragment key={domiciliaryGroup.groupKey}>
                        <TableRow>
                          <TableCell colSpan={12} sx={{ fontWeight: 700, color: "#4B2E1F", bgcolor: "#FAF1E8" }}>
                            Domiciliario: {domiciliaryGroup.nameDomiciliary} - {domiciliaryGroup.documentDomiciliary}
                          </TableCell>
                        </TableRow>

                        {domiciliaryGroup.rows.map((item) => (
                          <TableRow key={`${item.IdPointSale}-${item.IdDomiciliary}-${item.periodKey}`}>
                            <TableCell>{item.periodLabel}</TableCell>
                            <TableCell>{item.codePointSale} - {item.namePointSale}</TableCell>
                            <TableCell>{item.nameDomiciliary}</TableCell>
                            <TableCell>{item.documentDomiciliary}</TableCell>
                            <TableCell>{item.createdByUsers || "Sin información"}</TableCell>
                            <TableCell align="right">{formatCurrency(item.parameterValueSettlement)}</TableCell>
                            <TableCell align="right">{item.totalDeliveryQuantity}</TableCell>
                            <TableCell>{getAbsenceSummary(item.absenceTypes)}</TableCell>
                            <TableCell align="right">{item.totalAbsences}</TableCell>
                            <TableCell align="right">{formatCurrency(item.totalValueSettlement)}</TableCell>
                            <TableCell align="right">{item.totalRecords}</TableCell>

                            {canUpdateDeliveryQuantity && (
                              <TableCell align="center">
                                <Tooltip
                                  title={
                                    period === "day"
                                      ? "Editar registro"
                                      : "Solo se puede editar consultando por día"
                                  }
                                >
                                  <span>
                                    <IconButton
                                      size="small"
                                      onClick={() => handleOpenEditModal(item)}
                                      disabled={loadingReport || period !== "day" || !item.IdDeliveryRecord}
                                      sx={{
                                        color: "#4B2E1F",
                                        "&:hover": {
                                          bgcolor: "rgba(75, 46, 31, 0.08)",
                                        },
                                      }}
                                    >
                                      <EditOutlinedIcon fontSize="small" />
                                    </IconButton>
                                  </span>
                                </Tooltip>
                              </TableCell>
                            )}
                          </TableRow>
                        ))}

                        <TableRow>
                          <TableCell colSpan={6} sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                            Subtotal domiciliario: {domiciliaryGroup.nameDomiciliary}
                          </TableCell>
                          <TableCell align="right" sx={{ fontWeight: 800 }}>
                            {domiciliaryGroup.totalDeliveryQuantity}
                          </TableCell>
                          <TableCell sx={{ fontWeight: 800 }}>  
                          </TableCell>
                          <TableCell align="right" sx={{ fontWeight: 800 }}>
                            {domiciliaryGroup.totalAbsences}
                          </TableCell>
                          <TableCell align="right" sx={{ fontWeight: 800 }}>
                            {formatCurrency(domiciliaryGroup.totalValueSettlement)}
                          </TableCell>
                          <TableCell align="right" sx={{ fontWeight: 800 }}>
                            {domiciliaryGroup.totalRecords}
                          </TableCell>
                          {canUpdateDeliveryQuantity && <TableCell />}
                        </TableRow>
                      </Fragment>
                    ))}

                    <TableRow>
                      <TableCell colSpan={6} sx={{ fontWeight: 900, color: "#4B2E1F", bgcolor: "#F7E8D8" }}>
                        Subtotal punto de venta: {pointSaleGroup.codePointSale} - {pointSaleGroup.namePointSale}
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 900, bgcolor: "#F7E8D8" }}>
                        {pointSaleGroup.totalDeliveryQuantity}
                      </TableCell>
                      <TableCell sx={{ fontWeight: 900, bgcolor: "#F7E8D8" }}>                        
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 900, bgcolor: "#F7E8D8" }}>
                        {pointSaleGroup.totalAbsences}
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 900, bgcolor: "#F7E8D8" }}>
                        {formatCurrency(pointSaleGroup.totalValueSettlement)}
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 900, bgcolor: "#F7E8D8" }}>
                        {pointSaleGroup.totalRecords}
                      </TableCell>
                      {canUpdateDeliveryQuantity && <TableCell sx={{ bgcolor: "#F7E8D8" }} />}
                    </TableRow>
                  </Fragment>
                ))}

                {reportData.length > 0 && (
                  <TableRow>
                    <TableCell colSpan={6} sx={{ fontWeight: 900, color: "#FFFFFF", bgcolor: "#4B2E1F" }}>
                      TOTAL GENERAL
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 900, color: "#FFFFFF", bgcolor: "#4B2E1F" }}>
                      {totals.totalDeliveryQuantity}
                    </TableCell>
                    <TableCell sx={{ fontWeight: 900, color: "#FFFFFF", bgcolor: "#4B2E1F" }}>
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 900, color: "#FFFFFF", bgcolor: "#4B2E1F" }}>
                      {totals.totalAbsences}
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 900, color: "#FFFFFF", bgcolor: "#4B2E1F" }}>
                      {formatCurrency(totals.totalValueSettlement)}
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 900, color: "#FFFFFF", bgcolor: "#4B2E1F" }}>
                      {totals.totalRecords}
                    </TableCell>
                    {canUpdateDeliveryQuantity && <TableCell sx={{ bgcolor: "#4B2E1F" }} />}
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </Box>
        )}
      </Paper>

      <Dialog
        open={editModalOpen}
        onClose={handleCloseEditModal}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle
          sx={{
            color: "#4B2E1F",
            fontWeight: 700,
          }}
        >
          Editar registro de domicilio
        </DialogTitle>

        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {editingRow && (
              <Paper
                elevation={0}
                sx={{
                  border: "1px solid #E0CDBB",
                  borderRadius: 2,
                  p: 2,
                  bgcolor: "#FFF8EF",
                }}
              >
                <Typography sx={{ color: "#4B2E1F", fontWeight: 700 }}>
                  {editingRow.nameDomiciliary}
                </Typography>

                <Typography sx={{ color: "#8B6A55", fontSize: 14 }}>
                  Documento: {editingRow.documentDomiciliary}
                </Typography>

                <Typography sx={{ color: "#8B6A55", fontSize: 14 }}>
                  Punto de venta: {editingRow.codePointSale} - {editingRow.namePointSale}
                </Typography>

                <Typography sx={{ color: "#8B6A55", fontSize: 14 }}>
                  Fecha / periodo: {editingRow.periodLabel}
                </Typography>

                <Typography sx={{ color: "#8B6A55", fontSize: 14 }}>
                  Valor actual: {formatCurrency(editingRow.totalValueSettlement)}
                </Typography>
              </Paper>
            )}

            {editValidationError && (
              <Alert severity="warning">{editValidationError}</Alert>
            )}

            <RadioGroup
              row
              value={editRecordMode}
              onChange={(event) => {
                const mode = event.target.value as EditRecordMode;

                setEditRecordMode(mode);
                setEditValidationError("");

                if (mode === "delivery") {
                  setEditingAbsenceTypeId(0);

                  if (!editingQuantity) {
                    setEditingQuantity("1");
                  }
                }

                if (mode === "absence") {
                  setEditingQuantity("");
                }
              }}
            >
              <FormControlLabel
                value="delivery"
                control={<Radio />}
                label="Domicilios"
                disabled={savingQuantity}
              />

              <FormControlLabel
                value="absence"
                control={<Radio />}
                label="Ausentismo"
                disabled={savingQuantity}
              />
            </RadioGroup>

            {editRecordMode === "delivery" && (
              <TextField
                label="Nueva cantidad de domicilios"
                type="number"
                value={editingQuantity}
                disabled={savingQuantity}
                fullWidth
                onChange={(event) => setEditingQuantity(event.target.value)}
                slotProps={{
                  htmlInput: {
                    min: 1,
                    step: 1,
                  },
                }}
              />
            )}

            {editRecordMode === "absence" && (
              <TextField
                select
                label="Tipo de ausentismo"
                value={editingAbsenceTypeId}
                disabled={savingQuantity || loadingAbsenceTypes}
                fullWidth
                onChange={(event) =>
                  setEditingAbsenceTypeId(Number(event.target.value))
                }
              >
                <MenuItem value={0}>Selecciona un tipo de ausentismo</MenuItem>

                {absenceTypes.map((item) => (
                  <MenuItem key={item.IdAbsenceType} value={item.IdAbsenceType}>
                    {item.nameAbsenceType}
                  </MenuItem>
                ))}
              </TextField>
            )}

            {editingRow && editRecordMode === "delivery" && (
              <Alert severity="info">
                El valor total se recalculará automáticamente con el valor unitario actual de{" "}
                {formatCurrency(editingRow.parameterValueSettlement)}.
              </Alert>
            )}
            {editingRow && editRecordMode === "absence" && (
              <Alert severity="info">
                Al guardar como ausentismo, la cantidad de domicilios quedará en 0 y la liquidación asociada quedará sin valor.
              </Alert>
            )}
          </Stack>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            onClick={handleCloseEditModal}
            disabled={savingQuantity}
            sx={{
              color: "#4B2E1F",
              textTransform: "none",
            }}
          >
            Cancelar
          </Button>

          <Button
            variant="contained"
            onClick={handleSaveQuantity}
            disabled={savingQuantity}
            sx={{
              bgcolor: "#4B2E1F",
              color: "#FFFFFF",
              textTransform: "none",
              fontWeight: 600,
              "&:hover": {
                bgcolor: "#3A2318",
              },
            }}
          >
            {savingQuantity ? "Guardando..." : "Guardar cambios"}
          </Button>
        </DialogActions>
      </Dialog>

      <ResponseModal
        open={responseModal.open}
        severity={responseModal.severity}
        title={responseModal.title}
        message={responseModal.message}
        onClose={closeResponseModal}
      />
    </Stack>
  );
}