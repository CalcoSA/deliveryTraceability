import { Alert, Box, Button, Chip, CircularProgress, Paper, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography, Dialog, DialogActions, DialogContent, DialogTitle, FormControlLabel, Switch, TextField } from "@mui/material";
import { ResponseModal, type ResponseModalSeverity, } from "../components/ResponseModal";
import AddBusinessOutlinedIcon from "@mui/icons-material/AddBusinessOutlined";
import StorefrontOutlinedIcon from "@mui/icons-material/StorefrontOutlined";
import type { PointSale, PointSaleCreate  } from "../models/PointSale";
import CloseOutlinedIcon from "@mui/icons-material/CloseOutlined";
import { pointSaleService } from "../services/pointSaleService";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import SaveOutlinedIcon from "@mui/icons-material/SaveOutlined";
import { getErrorMessage } from "../services/errorService";
import { useEffect, useState } from "react";

type ModalMode = "create" | "update";

const emptyForm: PointSaleCreate = {
  codePointSale: "",
  namePointSale: "",
  statusPointSale: true,
};

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

export function PointSalePage() {
  const [responseModal, setResponseModal] = useState<ResponseModalState>(emptyResponseModal);
  const [selectedPointSale, setSelectedPointSale] = useState<PointSale | null>(null);
  const [loadingPointSaleId, setLoadingPointSaleId] = useState<number | null>(null);
  const [modalMode, setModalMode] = useState<ModalMode>("create");
  const [pointSales, setPointSales] = useState<PointSale[]>([]);
  const [form, setForm] = useState<PointSaleCreate>(emptyForm);
  const [validationError, setValidationError] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const isCreate = modalMode === "create";

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

  const loadPointSales = async (showError = true) => {
    try {
      setLoading(true);
      const response = await pointSaleService.getAll();
      setPointSales(response.result ?? []);
    } catch (err) {
      setPointSales([]);
      if (showError) {
        showResponseModal(
          "error",
          "Error al cargar",
          getErrorMessage(err)
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const openCreateModal = () => {
    setValidationError("");
    setSelectedPointSale(null);
    setForm(emptyForm);
    setModalMode("create");
    setModalOpen(true);
  };

  const openUpdateModal = async (idPointSale: number) => {
    try {
      setValidationError("");
      setLoadingPointSaleId(idPointSale);
      const response = await pointSaleService.getById(idPointSale);
      if (!response.isSuccess || !response.result) {
        showResponseModal(
          "error",
          "No se pudo obtener",
          response.Message || "No se pudo obtener el punto de venta."
        );
        return;
      }
      setSelectedPointSale(response.result);
      setForm({
        codePointSale: response.result.codePointSale,
        namePointSale: response.result.namePointSale,
        statusPointSale: response.result.statusPointSale,
      });
      setModalMode("update");
      setModalOpen(true);
    } catch (err) {
      showResponseModal(
        "error",
        "Error al consultar",
        getErrorMessage(err)
      );
    } finally {
      setLoadingPointSaleId(null);
    }
  };

  const closeModal = () => {
    if (saving) return;
    setModalOpen(false);
    setSelectedPointSale(null);
    setForm(emptyForm);
    setValidationError("");
  };

  const handleSubmitPointSale = async () => {
    try {
      const codePointSale = form.codePointSale.trim();
      const namePointSale = form.namePointSale.trim();
      if (!codePointSale) {
        setValidationError("El código del punto de venta es obligatorio.");
        return;
      }
      if (!namePointSale) {
        setValidationError("El nombre del punto de venta es obligatorio.");
        return;
      }
      setSaving(true);
      setValidationError("");
      const data: PointSaleCreate = {
        codePointSale,
        namePointSale,
        statusPointSale: form.statusPointSale,
      };
      const response =
        modalMode === "create"
          ? await pointSaleService.create(data)
          : await pointSaleService.update(
              selectedPointSale!.IdPointSale,
              data
            );
      if (!response.isSuccess) {
        showResponseModal(
          "error",
          modalMode === "create"
            ? "No se pudo crear"
            : "No se pudo actualizar",
          response.Message ||
            `No se pudo ${
              modalMode === "create" ? "crear" : "actualizar"
            } el punto de venta.`
        );
        return;
      }
      setModalOpen(false);
      setSelectedPointSale(null);
      setForm(emptyForm);
      await loadPointSales(false);
      showResponseModal(
        "success",
        modalMode === "create"
          ? "Punto de venta creado"
          : "Punto de venta actualizado",
        response.Message ||
          `Punto de venta ${
            modalMode === "create" ? "creado" : "actualizado"
          } correctamente.`
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

  useEffect(() => {
    loadPointSales();
  }, []);

  return (
    <Stack spacing={3}>
      <Stack sx={{ display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center", }}>
        <Box>
          <Stack sx={{ display: "flex", flexDirection: "row", gap: 1.5, alignItems: "center", }}>
            <StorefrontOutlinedIcon sx={{ color: "#4B2E1F", fontSize: 30 }} />
            <Typography sx={{ color: "#4B2E1F", fontSize: 26, fontWeight: 700, }}>
              Puntos de Venta
            </Typography>
          </Stack>
        </Box>

        <Button
          variant="outlined"
          startIcon={<AddBusinessOutlinedIcon />}
          onClick={openCreateModal}
          disabled={loading || saving}
          sx={{ borderColor: "#8B6A55", color: "#4B2E1F", "&:hover": { borderColor: "#4B2E1F", bgcolor: "rgba(75, 46, 31, 0.05)", },}}>
          Crear punto de venta
        </Button>
      </Stack>

      <Paper
        elevation={0}
        sx={{ border: "1px solid #E0CDBB", borderRadius: 2, overflow: "hidden", }}>
        {loading ? (
          <Box sx={{ py: 6, display: "flex", justifyContent: "center", }}>
            <CircularProgress sx={{ color: "#4B2E1F" }} />
          </Box>
        ) : (
          <Table>

            <TableHead>
              <TableRow sx={{ bgcolor: "#F7E8D8", }}>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  ID
                </TableCell>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Código
                </TableCell>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Punto de Venta
                </TableCell>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Estado
                </TableCell>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }} align="center">
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {pointSales.map((item) => {
                const isLoadingThisRow = loadingPointSaleId === item.IdPointSale;
                return (
                  <TableRow key={item.IdPointSale} hover>
                    <TableCell>{item.IdPointSale}</TableCell>
                    <TableCell>{item.codePointSale}</TableCell>
                    <TableCell>{item.namePointSale}</TableCell>
                    <TableCell>
                      <Chip
                        label={item.statusPointSale ? "Activo" : "Inactivo"}
                        size="small"
                        sx={{ bgcolor: item.statusPointSale ? "#E8F5E9" : "#FFEBEE", color: item.statusPointSale ? "#2E7D32" : "#C62828", fontWeight: 600, }}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={ isLoadingThisRow ? ( <CircularProgress size={16} /> ) : ( <EditOutlinedIcon /> ) }
                        onClick={() => openUpdateModal(item.IdPointSale)}
                        disabled={saving || loadingPointSaleId !== null}
                        sx={{ borderColor: "#8B6A55", color: "#4B2E1F", textTransform: "none", fontWeight: 600, "&:hover": { borderColor: "#4B2E1F", bgcolor: "rgba(75, 46, 31, 0.05)", },}}>
                        { isLoadingThisRow ? "Cargando..." : "Actualizar" }
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}

              {pointSales.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} align="center" sx={{ py: 4 }}>
                    No hay puntos de venta para mostrar.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </Paper>

      <Dialog open={modalOpen} onClose={saving ? undefined : closeModal} fullWidth maxWidth="sm">
        <DialogTitle sx={{ display: "flex", alignItems: "center", gap: 1, color: "#4B2E1F", fontWeight: 700, }}>
          {isCreate ? <AddBusinessOutlinedIcon /> : <EditOutlinedIcon />}
          {isCreate ? "Crear punto de venta" : "Actualizar punto de venta"}
        </DialogTitle>

        <DialogContent>
          
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <Typography sx={{ color: "#6B4A3A", fontSize: 14 }}>
              {isCreate
                ? "Completa la información para registrar un nuevo punto de venta."
                : "Modifica la información del punto de venta seleccionado."}
            </Typography>

            {validationError && (
              <Alert severity="warning">{validationError}</Alert>
            )}

            <TextField
              label="Código"
              value={form.codePointSale}
              disabled={saving}
              fullWidth
              required
              onChange={(event) =>
                setForm((prev) => ({
                  ...prev,
                  codePointSale: event.target.value,
                }))
              }
            />

            <TextField
              label="Nombre punto de venta"
              value={form.namePointSale}
              disabled={saving}
              fullWidth
              required
              onChange={(event) =>
                setForm((prev) => ({
                  ...prev,
                  namePointSale: event.target.value,
                }))
              }
            />

            <FormControlLabel
              control={
                <Switch
                  checked={form.statusPointSale}
                  disabled={saving}
                  onChange={(event) =>
                    setForm((prev) => ({
                      ...prev,
                      statusPointSale: event.target.checked,
                    }))
                  }
                />
              }
              label={form.statusPointSale ? "Activo" : "Inactivo"}
            />
          </Stack>

        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            variant="outlined"
            startIcon={<CloseOutlinedIcon />}
            onClick={closeModal}
            disabled={saving}
            sx={{ borderColor: "#8B6A55", color: "#4B2E1F", textTransform: "none", fontWeight: 600, "&:hover": { borderColor: "#4B2E1F", bgcolor: "rgba(75, 46, 31, 0.05)", },}}>
            Cancelar
          </Button>

          <Button
            variant="contained"
            startIcon={<SaveOutlinedIcon />}
            onClick={handleSubmitPointSale}
            disabled={saving}
            sx={{ bgcolor: "#4B2E1F", color: "#FFFFFF", textTransform: "none", fontWeight: 600, "&:hover": { bgcolor: "#3A2318", },}}>
            {saving ? "Guardando..." : isCreate ? "Crear" : "Actualizar"}
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