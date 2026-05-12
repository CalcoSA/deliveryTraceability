import { Alert, Box, Button, Chip, CircularProgress, InputAdornment, MenuItem, Paper, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography, } from "@mui/material";
import { ResponseModal, type ResponseModalSeverity, } from "../components/ResponseModal";
import CleaningServicesOutlinedIcon from "@mui/icons-material/CleaningServicesOutlined";
import CalendarMonthOutlinedIcon from "@mui/icons-material/CalendarMonthOutlined";
import AssignmentOutlinedIcon from "@mui/icons-material/AssignmentOutlined";
import StorefrontOutlinedIcon from "@mui/icons-material/StorefrontOutlined";
import { deliveryRecordService } from "../services/deliveryRecordService";
import { domiciliaryService } from "../services/domiciliaryService";
import { absenceTypeService } from "../services/absenceTypeService";
import { pointSaleService } from "../services/pointSaleService";
import SaveOutlinedIcon from "@mui/icons-material/SaveOutlined";
import type { AbsenceType } from "../models/DeliveryRecord";
import { getErrorMessage } from "../services/errorService";
import type { Domiciliary } from "../models/Domiciliary";
import type { PointSale } from "../models/PointSale";
import { useEffect, useState } from "react";

interface DomiciliaryDeliveryRow {
  IdDomiciliary: number;
  documentDomiciliary: string;
  nameDomiciliary: string;
  deliveryQuantity: string;
  IdAbsenceType: number | null;
}

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

export function DeliveryRegistrationPage() {
  const [responseModal, setResponseModal] = useState<ResponseModalState>(emptyResponseModal);
  const [selectedPointSaleId, setSelectedPointSaleId] = useState<number>(0);
  const [loadingDomiciliaries, setLoadingDomiciliaries] = useState(false);
  const [loadingAbsenceTypes, setLoadingAbsenceTypes] = useState(false);
  const [absenceTypes, setAbsenceTypes] = useState<AbsenceType[]>([]);
  const [loadingPointSales, setLoadingPointSales] = useState(false);
  const [rows, setRows] = useState<DomiciliaryDeliveryRow[]>([]);
  const [pointSales, setPointSales] = useState<PointSale[]>([]);
  const [deliveryDate, setDeliveryDate] = useState(getToday());
  const [validationError, setValidationError] = useState("");
  const [saving, setSaving] = useState(false);

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

  const loadAbsenceTypes = async () => {
    try {
      setLoadingAbsenceTypes(true);
      const response = await absenceTypeService.getAll();
      setAbsenceTypes(response.result ?? []);
    } catch (err) {
      setAbsenceTypes([]);
      showResponseModal(
        "error",
        "Error al cargar ausentismos",
        getErrorMessage(err)
      );
    } finally {
      setLoadingAbsenceTypes(false);
    }
  };

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
      setRows([]);
      if (!idPointSale || idPointSale <= 0) {
        return;
      }
      setLoadingDomiciliaries(true);
      const response = await domiciliaryService.getAll({
        pointSale: idPointSale,
        statusDomiciliary: true,
      });
      const domiciliaries = response.result ?? [];
      setRows(
        domiciliaries.map((item: Domiciliary) => ({
          IdDomiciliary: item.IdDomiciliary,
          documentDomiciliary: item.documentDomiciliary,
          nameDomiciliary: item.nameDomiciliary,
          deliveryQuantity: "",
          IdAbsenceType: null,
        }))
      );
    } catch (err) {
      setRows([]);
      showResponseModal(
        "error",
        "Error al cargar domiciliarios",
        getErrorMessage(err)
      );
    } finally {
      setLoadingDomiciliaries(false);
    }
  };

  const handleClearForm = () => {
    if (saving) return;
    setDeliveryDate(getToday());
    setSelectedPointSaleId(0);
    setRows([]);
    setValidationError("");
  };

  const handleChangePointSale = (idPointSale: number) => {
    setSelectedPointSaleId(idPointSale);
    setValidationError("");
    loadDomiciliariesByPointSale(idPointSale);
  };

  const updateRowQuantity = (idDomiciliary: number, value: string) => {
    const onlyNumbers = value.replace(/\D/g, "");
    setRows((prev) =>
      prev.map((item) =>
        item.IdDomiciliary === idDomiciliary
          ? {
              ...item,
              deliveryQuantity: onlyNumbers,
            }
          : item
      )
    );
  };

  const validateRowsBeforeSave = () => {
    if (!deliveryDate) {
      return "La fecha es obligatoria.";
    }
    if (!selectedPointSaleId || selectedPointSaleId <= 0) {
      return "Debes seleccionar un punto de venta.";
    }
    if (rows.length === 0) {
      return "El punto de venta seleccionado no tiene domiciliarios activos.";
    }
    const pendingRows = rows.filter((item) => {
      if (item.IdAbsenceType) return false;
      const quantity = Number(item.deliveryQuantity);
      return !item.deliveryQuantity || Number.isNaN(quantity) || quantity <= 0;
    });
    if (pendingRows.length > 0) {
      return "Debes ingresar el número de domicilios o marcar descanso para todos los domiciliarios.";
    }
    return "";
  };

  const updateRowAbsenceType = (idDomiciliary: number, idAbsenceType: number | null) => {
    setRows((prev) =>
      prev.map((item) =>
        item.IdDomiciliary === idDomiciliary
          ? {
              ...item,
              IdAbsenceType: idAbsenceType,
              deliveryQuantity: idAbsenceType ? "0" : item.deliveryQuantity,
            }
          : item
      )
    );
  };

  const handleSaveDeliveryRecords = async () => {
    try {
      const error = validateRowsBeforeSave();
      if (error) {
        setValidationError(error);
        return;
      }
      setSaving(true);
      setValidationError("");
      const response = await deliveryRecordService.createBulk({
        deliveryDate,
        IdPointSale: selectedPointSaleId,
        records: rows.map((item) => ({
          IdDomiciliary: item.IdDomiciliary,
          deliveryQuantity: item.IdAbsenceType ? 0 : Number(item.deliveryQuantity),
          IdAbsenceType: item.IdAbsenceType,
        })),
      });
      if (!response.isSuccess) {
        showResponseModal(
          "error",
          "No se pudo guardar",
          response.Message || "No se pudieron guardar los registros."
        );
        return;
      }
      handleClearForm();
      showResponseModal(
        "success",
        "Registros guardados",
        response.Message || "Registros de domicilios creados correctamente."
      );
    } catch (err) {
      showResponseModal(
        "error",
        "Error en la operación",
        getErrorMessage(err)
      );
    } finally {
      setSaving(false);
    }
  };

  const completedRows = rows.filter(
    (item) => item.IdAbsenceType || Number(item.deliveryQuantity) > 0
  ).length;

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
          gap: 1.5,
          alignItems: "center",
        }}
      >
        <AssignmentOutlinedIcon sx={{ color: "#4B2E1F", fontSize: 30 }} />

        <Typography
          sx={{
            color: "#4B2E1F",
            fontSize: 26,
            fontWeight: 700,
          }}
        >
          Registro de domicilios
        </Typography>
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
            Información del registro
          </Typography>

          {validationError && <Alert severity="warning">{validationError}</Alert>}

          <Stack
            sx={{
              display: "flex",
              flexDirection: { xs: "column", md: "row" },
              gap: 2,
            }}
          >
            <TextField
              label="Fecha"
              type="date"
              value={deliveryDate}
              disabled={saving}
              fullWidth
              onChange={(event) => setDeliveryDate(event.target.value)}
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
              label="Punto de venta"
              value={selectedPointSaleId}
              disabled={saving || loadingPointSales}
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
              <MenuItem value={0}>Seleccione un punto de venta</MenuItem>

              {pointSales.map((item) => (
                <MenuItem key={item.IdPointSale} value={item.IdPointSale}>
                  {item.codePointSale} - {item.namePointSale}
                </MenuItem>
              ))}
            </TextField>

            <Button
              variant="outlined"
              onClick={handleClearForm}
              disabled={saving}
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
                saving ? (
                  <CircularProgress size={16} sx={{ color: "#FFFFFF" }} />
                ) : (
                  <SaveOutlinedIcon />
                )
              }
              onClick={handleSaveDeliveryRecords}
              disabled={saving || loadingDomiciliaries || rows.length === 0}
              sx={{
                minWidth: { xs: "100%", md: 190 },
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
              {saving ? "Guardando..." : "Guardar registros"}
            </Button>
          </Stack>

          {rows.length > 0 && (
            <Stack
              sx={{
                display: "flex",
                flexDirection: "row",
                gap: 1,
                alignItems: "center",
              }}
            >
              <Chip
                label={`${completedRows} de ${rows.length} diligenciados`}
                size="small"
                sx={{
                  bgcolor:
                    completedRows === rows.length ? "#E8F5E9" : "#FFF4E5",
                  color:
                    completedRows === rows.length ? "#2E7D32" : "#ED6C02",
                  fontWeight: 600,
                }}
              />

              <Typography sx={{ color: "#6B4A3A", fontSize: 14 }}>
                Debes ingresar domicilios o marcar descanso para todos.
              </Typography>
            </Stack>
          )}
        </Stack>
      </Paper>

      <Paper
        elevation={0}
        sx={{
          border: "1px solid #E0CDBB",
          borderRadius: 2,
          overflow: "hidden",
        }}
      >
        {loadingDomiciliaries ? (
          <Box
            sx={{
              py: 6,
              display: "flex",
              justifyContent: "center",
            }}
          >
            <CircularProgress sx={{ color: "#4B2E1F" }} />
          </Box>
        ) : (
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: "#F7E8D8" }}>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Documento
                </TableCell>

                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Domiciliario
                </TableCell>

                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Número de domicilios
                </TableCell>

                <TableCell
                  align="center"
                  sx={{ fontWeight: 700, color: "#4B2E1F" }}
                >
                  Descanso
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {rows.map((item) => (
                <TableRow key={item.IdDomiciliary} hover>
                  <TableCell>{item.documentDomiciliary}</TableCell>

                  <TableCell>{item.nameDomiciliary}</TableCell>

                  <TableCell sx={{ width: 260 }}>
                    <TextField
                      label="Domicilios"
                      value={item.deliveryQuantity}
                      disabled={saving || Boolean(item.IdAbsenceType)}
                      fullWidth
                      size="small"
                      placeholder={item.IdAbsenceType ? "0" : "Ej: 10"}
                      onChange={(event) =>
                        updateRowQuantity(item.IdDomiciliary, event.target.value)
                      }
                    />
                  </TableCell>

                  <TableCell align="center">
                    <TextField
                      select
                      label="Ausentismo"
                      value={item.IdAbsenceType ?? 0}
                      fullWidth
                      size="small"
                      disabled={saving || loadingAbsenceTypes}
                      onChange={(event) => {
                        const value = Number(event.target.value);

                        updateRowAbsenceType(
                          item.IdDomiciliary,
                          value > 0 ? value : null
                        );
                      }}
                    >
                      <MenuItem value={0}>Sin ausentismo</MenuItem>

                      {absenceTypes.map((absenceType) => (
                        <MenuItem
                          key={absenceType.IdAbsenceType}
                          value={absenceType.IdAbsenceType}
                        >
                          {absenceType.nameAbsenceType}
                        </MenuItem>
                      ))}
                    </TextField>
                  </TableCell>
                </TableRow>
              ))}

              {rows.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} align="center" sx={{ py: 4 }}>
                    Selecciona un punto de venta para cargar sus domiciliarios.
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