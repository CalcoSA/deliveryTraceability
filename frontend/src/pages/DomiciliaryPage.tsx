import { Alert, Box, Button, Chip, CircularProgress, Dialog, DialogActions, DialogContent, DialogTitle, FormControlLabel, InputAdornment, MenuItem, Paper, Stack, Switch, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography, } from "@mui/material";
import { ResponseModal, type ResponseModalSeverity, } from "../components/ResponseModal";
import CleaningServicesOutlinedIcon from "@mui/icons-material/CleaningServicesOutlined";
import LocalShippingOutlinedIcon from "@mui/icons-material/LocalShippingOutlined";
import PersonAddAlt1OutlinedIcon from "@mui/icons-material/PersonAddAlt1Outlined";
import type { Domiciliary, DomiciliaryCreate } from "../models/Domiciliary";
import { domiciliaryService } from "../services/domiciliaryService";
import SearchOutlinedIcon from "@mui/icons-material/SearchOutlined";
import CloseOutlinedIcon from "@mui/icons-material/CloseOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import SaveOutlinedIcon from "@mui/icons-material/SaveOutlined";
import { pointSaleService } from "../services/pointSaleService";
import { getErrorMessage } from "../services/errorService";
import type { PointSale } from "../models/PointSale";
import { useEffect, useRef, useState } from "react";

type ModalMode = "create" | "update";

const emptyForm: DomiciliaryCreate = {
  documentDomiciliary: "",
  nameDomiciliary: "",
  statusDomiciliary: true,
  pointSale: 0,
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

export function DomiciliaryPage() {
  const [responseModal, setResponseModal] = useState<ResponseModalState>(emptyResponseModal);
  const [selectedDomiciliary, setSelectedDomiciliary] = useState<Domiciliary | null>(null);
  const [loadingDomiciliaryId, setLoadingDomiciliaryId] = useState<number | null>(null);
  const [filterStatus, setFilterStatus] = useState<"all" | "true" | "false">("all");
  const [domiciliaries, setDomiciliaries] = useState<Domiciliary[]>([]);
  const [filterPointSale, setFilterPointSale] = useState<number>(0);
  const [modalMode, setModalMode] = useState<ModalMode>("create");
  const [form, setForm] = useState<DomiciliaryCreate>(emptyForm);
  const [pointSales, setPointSales] = useState<PointSale[]>([]);
  const [validationError, setValidationError] = useState("");
  const [searchDocument, setSearchDocument] = useState(""); 
  const [modalOpen, setModalOpen] = useState(false);
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const isCreate = modalMode === "create";
  const firstSearchRender = useRef(true);

  const getOnlyNumbers = (value: string) => {
    return value.replace(/\D/g, "").slice(0, 15);
  };

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

  const getDomiciliaryFilters = () => {
    return {
      pointSale: filterPointSale > 0 ? filterPointSale : undefined,
      statusDomiciliary: filterStatus === "all" ? undefined : filterStatus === "true",
    };
  };

  const clearFilters = () => {
    setSearchDocument("");
    setFilterPointSale(0);
    setFilterStatus("all");
  };

  const loadDomiciliaries = async (showError = true) => {
    try {
      setLoading(true);
      const response = await domiciliaryService.getAll(getDomiciliaryFilters());
      setDomiciliaries(response.result ?? []);
    } catch (err) {
      setDomiciliaries([]);
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

  const loadPointSales = async () => {
    try {
      const response = await pointSaleService.getAll();
      setPointSales(response.result ?? []);
    } catch (err) {
      setPointSales([]);
      showResponseModal(
        "error",
        "Error al cargar puntos de venta",
        getErrorMessage(err)
      );
    }
  };

  const searchDomiciliaryByDocument = async (documentDomiciliary: string) => {
    try {
      setSearching(true);
      const response = await domiciliaryService.getByDocument(documentDomiciliary);
      if (!response.isSuccess || !response.result) {
        setDomiciliaries([]);
        return;
      }
      const domiciliaryFound = response.result;
      const matchesPointSale = filterPointSale === 0 || domiciliaryFound.pointSale === filterPointSale;
      const matchesStatus = filterStatus === "all" || domiciliaryFound.statusDomiciliary === (filterStatus === "true");

      if (!matchesPointSale || !matchesStatus) {
        setDomiciliaries([]);
        return;
      }
      setDomiciliaries([domiciliaryFound]);
    } catch {
      setDomiciliaries([]);
    } finally {
      setSearching(false);
    }
  };

  const getPointSaleLabel = (idPointSale: number) => {
    const pointSale = pointSales.find(
      (item) => item.IdPointSale === idPointSale
    );
    if (!pointSale) return idPointSale;
    return `${pointSale.codePointSale} - ${pointSale.namePointSale}`;
  };

  const openCreateModal = () => {
    setValidationError("");
    setSelectedDomiciliary(null);
    setForm(emptyForm);
    setModalMode("create");
    setModalOpen(true);
  };

  const openUpdateModal = async (idDomiciliary: number) => {
    try {
      setValidationError("");
      setLoadingDomiciliaryId(idDomiciliary);
      const response = await domiciliaryService.getById(idDomiciliary);
      if (!response.isSuccess || !response.result) {
        showResponseModal(
          "error",
          "No se pudo obtener",
          response.Message || "No se pudo obtener el domiciliario."
        );
        return;
      }
      setSelectedDomiciliary(response.result);
      setForm({
        documentDomiciliary: response.result.documentDomiciliary,
        nameDomiciliary: response.result.nameDomiciliary,
        statusDomiciliary: response.result.statusDomiciliary,
        pointSale: response.result.pointSale,
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
      setLoadingDomiciliaryId(null);
    }
  };

  const closeModal = () => {
    if (saving) return;
    setModalOpen(false);
    setSelectedDomiciliary(null);
    setForm(emptyForm);
    setValidationError("");
  };

  const refreshDomiciliariesAfterSave = async () => {
    const documentToSearch = searchDocument.trim();
    if (documentToSearch.length >= 3) {
      await searchDomiciliaryByDocument(documentToSearch);
      return;
    }
    await loadDomiciliaries();
  };

  const handleSubmitDomiciliary = async () => {
    try {
      const documentDomiciliary = form.documentDomiciliary.trim();
      const nameDomiciliary = form.nameDomiciliary.trim();
      if (!documentDomiciliary) {
        setValidationError("El documento del domiciliario es obligatorio.");
        return;
      }
      if (!/^\d+$/.test(documentDomiciliary)) {
        setValidationError("El documento solo puede contener números.");
        return;
      }
      if (documentDomiciliary.length > 15) {
        setValidationError("El documento no puede tener más de 15 caracteres.");
        return;
      }
      if (!nameDomiciliary) {
        setValidationError("El nombre del domiciliario es obligatorio.");
        return;
      }
      if (!form.pointSale || form.pointSale <= 0) {
        setValidationError("Debes seleccionar un punto de venta.");
        return;
      }
      setSaving(true);
      setValidationError("");
      const data: DomiciliaryCreate = {
        documentDomiciliary,
        nameDomiciliary,
        statusDomiciliary: form.statusDomiciliary,
        pointSale: form.pointSale,
      };
      const response =
        modalMode === "create"
          ? await domiciliaryService.create(data)
          : await domiciliaryService.update(
              selectedDomiciliary!.IdDomiciliary,
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
            } el domiciliario.`
        );
        return;
      }
      setModalOpen(false);
      setSelectedDomiciliary(null);
      setForm(emptyForm);
      await refreshDomiciliariesAfterSave();
      showResponseModal(
        "success",
        modalMode === "create"
          ? "Domiciliario creado"
          : "Domiciliario actualizado",
        response.Message ||
          `Domiciliario ${
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
    loadDomiciliaries();
    loadPointSales();
  }, []);

  useEffect(() => {
    if (firstSearchRender.current) {
      firstSearchRender.current = false;
      return;
    }
    const documentToSearch = searchDocument.trim();
    const timeout = window.setTimeout(() => {
      if (documentToSearch.length >= 3) {
        searchDomiciliaryByDocument(documentToSearch);
        return;
      }
      loadDomiciliaries();
    }, 500);
    return () => window.clearTimeout(timeout);
  }, [searchDocument, filterPointSale, filterStatus]);

  return (
    <Stack spacing={3}>
      <Stack sx={{ display: "flex", flexDirection: "row", justifyContent: "space-between", alignItems: "center", }}>
        <Box>
          <Stack sx={{ display: "flex", flexDirection: "row", gap: 1.5, alignItems: "center", }}>
            <LocalShippingOutlinedIcon sx={{ color: "#4B2E1F", fontSize: 30 }}/>
            <Typography
              sx={{ color: "#4B2E1F", fontSize: 26, fontWeight: 700, }}>
              Domiciliarios
            </Typography>
          </Stack>
        </Box>

        <Button
          variant="outlined"
          startIcon={<PersonAddAlt1OutlinedIcon />}
          onClick={openCreateModal}
          disabled={loading || saving}
          sx={{ borderColor: "#8B6A55", color: "#4B2E1F", "&:hover": { borderColor: "#4B2E1F", bgcolor: "rgba(75, 46, 31, 0.05)", },}}>
          Crear domiciliario
        </Button>
      </Stack>

      <Stack sx={{ display: "flex", flexDirection: { xs: "column", md: "row" }, gap: 2, }}>
        <TextField
          label="Buscar por documento"
          value={searchDocument}
          fullWidth
          slotProps={{
            htmlInput: { maxLength: 15, inputMode: "numeric", pattern: "[0-9]*", },
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchOutlinedIcon sx={{ color: "#8B6A55" }} />
                </InputAdornment>
              ),
              endAdornment: searching ? (
                <InputAdornment position="end">
                  <CircularProgress size={18} sx={{ color: "#4B2E1F" }} />
                </InputAdornment>
              ) : undefined,
            },
          }}
          onChange={(event) => {
            setSearchDocument(getOnlyNumbers(event.target.value));
          }}
        />

        <TextField
          select
          label="Punto de venta"
          value={filterPointSale}
          fullWidth
          onChange={(event) => {
            setFilterPointSale(Number(event.target.value));
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
          label="Estado"
          value={filterStatus}
          fullWidth
          onChange={(event) => {
            setFilterStatus(event.target.value as "all" | "true" | "false");
          }}
        >
          <MenuItem value="all">Todos los estados</MenuItem>
          <MenuItem value="true">Activo</MenuItem>
          <MenuItem value="false">Inactivo</MenuItem>
        </TextField>

        <Button
          variant="outlined"
          startIcon={<CleaningServicesOutlinedIcon />}
          onClick={clearFilters}
          disabled={
            loading ||
            searching ||
            saving ||
            (searchDocument.trim() === "" &&
              filterPointSale === 0 &&
              filterStatus === "all")
          }
          sx={{
            minWidth: 100,
            width: 56,
            height: 56,
            p: 0,
            borderColor: "#8B6A55",
            color: "#4B2E1F",
            "&:hover": {
              borderColor: "#4B2E1F",
              bgcolor: "rgba(75, 46, 31, 0.05)",
            },
          }}
        > Limpiar
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
                  Documento
                </TableCell>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Nombre
                </TableCell>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Punto de Venta
                </TableCell>
                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Estado
                </TableCell>
                <TableCell
                  sx={{ fontWeight: 700, color: "#4B2E1F" }}
                  align="center"
                ></TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {domiciliaries.map((item) => {
                const isLoadingThisRow = loadingDomiciliaryId === item.IdDomiciliary;
                return (
                  <TableRow key={item.IdDomiciliary} hover>
                    <TableCell>{item.IdDomiciliary}</TableCell>
                    <TableCell>{item.documentDomiciliary}</TableCell>
                    <TableCell>{item.nameDomiciliary}</TableCell>
                    <TableCell>{getPointSaleLabel(item.pointSale)}</TableCell>
                    <TableCell>
                      <Chip
                        label={item.statusDomiciliary ? "Activo" : "Inactivo"}
                        size="small"
                        sx={{ bgcolor: item.statusDomiciliary ? "#E8F5E9" : "#FFEBEE", color: item.statusDomiciliary ? "#2E7D32" : "#C62828", fontWeight: 600, }}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={ isLoadingThisRow ? ( <CircularProgress size={16} /> ) : ( <EditOutlinedIcon /> ) }
                        onClick={() => openUpdateModal(item.IdDomiciliary)}
                        disabled={saving || loadingDomiciliaryId !== null}
                        sx={{ borderColor: "#8B6A55", color: "#4B2E1F", textTransform: "none", fontWeight: 600, "&:hover": { borderColor: "#4B2E1F", bgcolor: "rgba(75, 46, 31, 0.05)", },}}>
                        {isLoadingThisRow ? "Cargando..." : "Actualizar"}
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}

              {domiciliaries.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    No hay domiciliarios para mostrar.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </Paper>

      <Dialog open={modalOpen} onClose={saving ? undefined : closeModal} fullWidth maxWidth="sm">
        <DialogTitle sx={{ display: "flex", alignItems: "center", gap: 1, color: "#4B2E1F", fontWeight: 700, }}>
          {isCreate ? <PersonAddAlt1OutlinedIcon /> : <EditOutlinedIcon />}
          {isCreate ? "Crear domiciliario" : "Actualizar domiciliario"}
        </DialogTitle>

        <DialogContent>

          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <Typography sx={{ color: "#6B4A3A", fontSize: 14 }}>
              {isCreate
                ? "Completa la información para registrar un nuevo domiciliario."
                : "Modifica la información del domiciliario seleccionado."}
            </Typography>

            {validationError && (
              <Alert severity="warning">{validationError}</Alert>
            )}

            <TextField
              label="Documento"
              value={form.documentDomiciliary}
              disabled={saving}
              fullWidth
              required
              slotProps={{ htmlInput: { maxLength: 15, inputMode: "numeric", pattern: "[0-9]*", },}}
              onChange={(event) =>
                setForm((prev) => ({
                  ...prev,
                  documentDomiciliary: event.target.value.slice(0, 15),
                }))
              }
            />

            <TextField
              label="Nombre domiciliario"
              value={form.nameDomiciliary}
              disabled={saving}
              fullWidth
              required
              onChange={(event) =>
                setForm((prev) => ({
                  ...prev,
                  nameDomiciliary: event.target.value,
                }))
              }
            />

            <TextField
              select
              label="Punto de venta"
              value={form.pointSale}
              disabled={saving}
              fullWidth
              required
              onChange={(event) =>
                setForm((prev) => ({
                  ...prev,
                  pointSale: Number(event.target.value),
                }))
              }
            >
              <MenuItem value={0}>Seleccione un punto de venta</MenuItem>
              {pointSales.map((item) => (
                <MenuItem key={item.IdPointSale} value={item.IdPointSale}>
                  {item.codePointSale} - {item.namePointSale}
                </MenuItem>
              ))}
            </TextField>

            <FormControlLabel
              control={
                <Switch
                  checked={form.statusDomiciliary}
                  disabled={saving}
                  onChange={(event) =>
                    setForm((prev) => ({
                      ...prev,
                      statusDomiciliary: event.target.checked,
                    }))
                  }
                />
              }
              label={form.statusDomiciliary ? "Activo" : "Inactivo"}
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
            onClick={handleSubmitDomiciliary}
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