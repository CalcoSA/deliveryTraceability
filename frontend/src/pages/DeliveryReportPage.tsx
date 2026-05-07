import { Alert, Box, Button, Chip, CircularProgress, InputAdornment, MenuItem, Paper, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography, } from "@mui/material";
import type { DeliveryReportPeriod, DeliverySettlementReport, } from "../models/DeliveryReport";
import { ResponseModal, type ResponseModalSeverity, } from "../components/ResponseModal";
import CleaningServicesOutlinedIcon from "@mui/icons-material/CleaningServicesOutlined";
import DeliveryDiningOutlinedIcon from "@mui/icons-material/DeliveryDiningOutlined";
import CalendarMonthOutlinedIcon from "@mui/icons-material/CalendarMonthOutlined";
import FileDownloadOutlinedIcon from "@mui/icons-material/FileDownloadOutlined";
import AssessmentOutlinedIcon from "@mui/icons-material/AssessmentOutlined";
import StorefrontOutlinedIcon from "@mui/icons-material/StorefrontOutlined";
import { deliveryReportService } from "../services/deliveryReportService";
import SearchOutlinedIcon from "@mui/icons-material/SearchOutlined";
import { domiciliaryService } from "../services/domiciliaryService";
import { pointSaleService } from "../services/pointSaleService";
import { Fragment, useEffect, useMemo, useState } from "react";
import { getErrorMessage } from "../services/errorService";
import type { Domiciliary } from "../models/Domiciliary";
import type { PointSale } from "../models/PointSale";
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
  const [selectedDomiciliaryId, setSelectedDomiciliaryId] = useState<number>(0);
  const [reportData, setReportData] = useState<DeliverySettlementReport[]>([]);
  const [selectedPointSaleId, setSelectedPointSaleId] = useState<number>(0);  
  const [startDate, setStartDate] = useState(getFirstDayOfCurrentMonth());
  const [loadingDomiciliaries, setLoadingDomiciliaries] = useState(false);
  const [domiciliaries, setDomiciliaries] = useState<Domiciliary[]>([]);  
  const [loadingPointSales, setLoadingPointSales] = useState(false);
  const [period, setPeriod] = useState<DeliveryReportPeriod>("day");
  const [pointSales, setPointSales] = useState<PointSale[]>([]);
  const [validationError, setValidationError] = useState("");
  const [loadingReport, setLoadingReport] = useState(false);
  const [endDate, setEndDate] = useState(getToday());  

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

  const totals = useMemo(() => {
    return reportData.reduce(
      (acc, item) => {
        acc.totalDeliveryQuantity += Number(item.totalDeliveryQuantity ?? 0);
        acc.totalRestDays += Number(item.totalRestDays ?? 0);
        acc.totalValueSettlement += Number(item.totalValueSettlement ?? 0);
        acc.totalRecords += Number(item.totalRecords ?? 0);
        return acc;
      },
      {
        totalDeliveryQuantity: 0,
        totalRestDays: 0,
        totalValueSettlement: 0,
        totalRecords: 0,
      }
    );
  }, [reportData]);

  const parameterColumnName = reportData.find((item) => item.parameterNameSettlement) ?.parameterNameSettlement ?? "Parámetro";

  const groupedReportData = useMemo(() => {
    const sortedData = [...reportData].sort((a, b) => {
      const pointSaleCompare = `${a.codePointSale} ${a.namePointSale}`.localeCompare(
        `${b.codePointSale} ${b.namePointSale}`
      );

      if (pointSaleCompare !== 0) return pointSaleCompare;

      const periodCompare = a.periodKey.localeCompare(b.periodKey);

      if (periodCompare !== 0) return periodCompare;

      return a.nameDomiciliary.localeCompare(b.nameDomiciliary);
    });

    const groups: {
      groupKey: string;
      codePointSale: string;
      namePointSale: string;
      rows: DeliverySettlementReport[];
      subtotalDeliveryQuantity: number;
      subtotalRestDays: number;
      subtotalValueSettlement: number;
      subtotalRecords: number;
    }[] = [];

    sortedData.forEach((item) => {
      const groupKey = String(item.IdPointSale);

      let group = groups.find((current) => current.groupKey === groupKey);

      if (!group) {
        group = {
          groupKey,
          codePointSale: item.codePointSale,
          namePointSale: item.namePointSale,
          rows: [],
          subtotalDeliveryQuantity: 0,
          subtotalRestDays: 0,
          subtotalValueSettlement: 0,
          subtotalRecords: 0,
        };

        groups.push(group);
      }

      group.rows.push(item);
      group.subtotalDeliveryQuantity += Number(
        item.totalDeliveryQuantity ?? 0
      );
      group.subtotalRestDays += Number(item.totalRestDays ?? 0);
      group.subtotalValueSettlement += Number(item.totalValueSettlement ?? 0);
      group.subtotalRecords += Number(item.totalRecords ?? 0);
    });

    return groups;
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

  const handleExportReport = () => {
    if (reportData.length === 0) {
      showResponseModal(
        "warning",
        "Sin datos para exportar",
        "Primero debes consultar el reporte antes de exportarlo."
      );
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
      "Descansos",
      "Valor total",
      "Registros",
    ];

    const rows: (string | number)[][] = [];

    rows.push(["REPORTE DE DOMICILIOS"]);
    rows.push([`Fecha de generación: ${new Date().toLocaleString("es-CO")}`]);
    rows.push([
      `Filtros: ${startDate} a ${endDate} | Periodo: ${getPeriodLabel(period)}`,
    ]);
    rows.push([]);
    rows.push(columns);

    const groupHeaderRows: number[] = [];
    const subtotalRows: number[] = [];

    groupedReportData.forEach((group) => {
      groupHeaderRows.push(rows.length);

      rows.push([`${group.codePointSale} - ${group.namePointSale}`]);

      group.rows.forEach((item) => {
        rows.push([
          item.periodLabel,
          `${item.codePointSale} - ${item.namePointSale}`,
          item.nameDomiciliary,
          item.documentDomiciliary,
          item.createdByUsers || "Sin información",
          Number(item.parameterValueSettlement ?? 0),
          Number(item.totalDeliveryQuantity ?? 0),
          Number(item.totalRestDays ?? 0),
          Number(item.totalValueSettlement ?? 0),
          Number(item.totalRecords ?? 0),
        ]);
      });

      subtotalRows.push(rows.length);

      rows.push([
        "",
        "",
        `Subtotal ${group.codePointSale} - ${group.namePointSale}`,
        "",
        "",
        "",
        group.subtotalDeliveryQuantity,
        group.subtotalRestDays,
        group.subtotalValueSettlement,
        group.subtotalRecords,
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
      totals.totalRestDays,
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
      { wch: 12 },
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
      ref: `A5:J5`,
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
              Total descansos
            </Typography>
            <Typography sx={{ color: "#4B2E1F", fontSize: 26, fontWeight: 800 }}>
              {totals.totalRestDays}
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
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: "#F7E8D8" }}>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Periodo
                </TableCell>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Punto de venta
                </TableCell>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Domiciliario
                </TableCell>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Registrado por
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  {parameterColumnName}
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Domicilios
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Descansos
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Valor total
                </TableCell>
                <TableCell align="center" sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Registros
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {groupedReportData.map((group) => (
                <Fragment key={group.groupKey}>
                  <TableRow sx={{ bgcolor: "#FFF8EF" }}>
                    <TableCell
                      colSpan={9}
                      sx={{
                        color: "#4B2E1F",
                        fontWeight: 800,
                        borderTop: "1px solid #E0CDBB",
                      }}
                    >
                      {group.codePointSale} - {group.namePointSale}
                    </TableCell>
                  </TableRow>

                  {group.rows.map((item, index) => (
                    <TableRow
                      key={`${item.periodKey}-${item.IdPointSale}-${item.IdDomiciliary}-${index}`}
                      hover
                    >
                      <TableCell>
                        <Stack spacing={0.5}>
                          <Typography sx={{ fontWeight: 600 }}>
                            {item.periodLabel}
                          </Typography>
                          <Chip
                            label={getPeriodLabel(item.periodType)}
                            size="small"
                            sx={{
                              width: "fit-content",
                              bgcolor: "#F7E8D8",
                              color: "#4B2E1F",
                              fontWeight: 600,
                            }}
                          />
                        </Stack>
                      </TableCell>

                      <TableCell>
                        {item.codePointSale} - {item.namePointSale}
                      </TableCell>

                      <TableCell>
                        <Stack spacing={0.3}>
                          <Typography sx={{ fontWeight: 600 }}>
                            {item.nameDomiciliary}
                          </Typography>
                          <Typography sx={{ color: "#6B4A3A", fontSize: 13 }}>
                            {item.documentDomiciliary}
                          </Typography>
                        </Stack>
                      </TableCell>

                      <TableCell>{item.createdByUsers || "Sin información"}</TableCell>

                      <TableCell align="right">
                        {formatCurrency(item.parameterValueSettlement)}
                      </TableCell>

                      <TableCell align="right">
                        {item.totalDeliveryQuantity}
                      </TableCell>

                      <TableCell align="right">
                        {item.totalRestDays}
                      </TableCell>

                      <TableCell align="right">
                        {formatCurrency(item.totalValueSettlement)}
                      </TableCell>

                      <TableCell align="center">
                        {item.totalRecords}
                      </TableCell>
                    </TableRow>
                  ))}

                  <TableRow sx={{ bgcolor: "#F7E8D8" }}>
                    <TableCell colSpan={5} sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                      Subtotal {group.codePointSale} - {group.namePointSale}
                    </TableCell>

                    <TableCell align="right" sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                      {group.subtotalDeliveryQuantity}
                    </TableCell>

                    <TableCell align="right" sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                      {group.subtotalRestDays}
                    </TableCell>

                    <TableCell align="right" sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                      {formatCurrency(group.subtotalValueSettlement)}
                    </TableCell>

                    <TableCell align="center" sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                      {group.subtotalRecords}
                    </TableCell>
                  </TableRow>
                </Fragment>
              ))}

              {reportData.length === 0 && (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                    No hay datos para mostrar. Selecciona los filtros y consulta el reporte.
                  </TableCell>
                </TableRow>
              )}

              {reportData.length > 0 && (
                <TableRow sx={{ bgcolor: "#FFF8EF" }}>
                  <TableCell colSpan={5} sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                    Total general
                  </TableCell>

                  <TableCell align="right" sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                    {totals.totalDeliveryQuantity}
                  </TableCell>

                  <TableCell align="right" sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                    {totals.totalRestDays}
                  </TableCell>

                  <TableCell align="right" sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                    {formatCurrency(totals.totalValueSettlement)}
                  </TableCell>

                  <TableCell align="center" sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                    {totals.totalRecords}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </Paper>

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