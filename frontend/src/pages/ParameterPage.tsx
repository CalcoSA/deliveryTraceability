import { Alert, Box, Button, CircularProgress, Dialog, DialogActions, DialogContent, DialogTitle, Paper, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography, } from "@mui/material";
import { ResponseModal, type ResponseModalSeverity, } from "../components/ResponseModal";
import AddCircleOutlineOutlinedIcon from "@mui/icons-material/AddCircleOutlineOutlined";
import type { Parameter, ParameterCreate, ParameterUpdate } from "../models/Parameter";
import CloseOutlinedIcon from "@mui/icons-material/CloseOutlined";
import TuneOutlinedIcon from "@mui/icons-material/TuneOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import SaveOutlinedIcon from "@mui/icons-material/SaveOutlined";
import { parameterService } from "../services/parameterService";
import { getErrorMessage } from "../services/errorService";
import { useEffect, useState } from "react";

type ModalMode = "create" | "update";

interface ParameterForm {
  nameParameter: string;
  valueParameter: string;
}

interface ResponseModalState {
  open: boolean;
  severity: ResponseModalSeverity;
  title: string;
  message: string;
}

const emptyForm: ParameterForm = {
  nameParameter: "",
  valueParameter: "",
};

const emptyResponseModal: ResponseModalState = {
  open: false,
  severity: "info",
  title: "",
  message: "",
};

export function ParameterPage() {
  const [responseModal, setResponseModal] = useState<ResponseModalState>(emptyResponseModal);
  const [selectedParameter, setSelectedParameter] = useState<Parameter | null>(null);
  const [loadingParameterId, setLoadingParameterId] = useState<number | null>(null);
  const [parameterModalOpen, setParameterModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<ModalMode>("create");
  const [parameters, setParameters] = useState<Parameter[]>([]);
  const [form, setForm] = useState<ParameterForm>(emptyForm);
  const [validationError, setValidationError] = useState("");
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

  const formatDate = (value: string | null) => {
    if (!value) return "Sin modificación";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleString("es-CO", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const loadParameters = async () => {
    try {
      setLoading(true);
      const response = await parameterService.getAll();
      setParameters(response.result ?? []);
    } catch (err) {
      setParameters([]);
      showResponseModal(
        "error",
        "Error al cargar",
        getErrorMessage(err)
      );
    } finally {
      setLoading(false);
    }
  };

  const openCreateModal = () => {
    setValidationError("");
    setSelectedParameter(null);
    setForm(emptyForm);
    setModalMode("create");
    setParameterModalOpen(true);
  };

  const openUpdateModal = (parameter: Parameter) => {
    setValidationError("");
    setLoadingParameterId(parameter.IdParameter);
    setSelectedParameter(parameter);
    setForm({
      nameParameter: parameter.nameParameter,
      valueParameter: parameter.valueParameter,
    });
    setModalMode("update");
    setParameterModalOpen(true);
    setLoadingParameterId(null);
  };

  const closeParameterModal = () => {
    if (saving) return;
    setParameterModalOpen(false);
    setSelectedParameter(null);
    setForm(emptyForm);
    setValidationError("");
  };

  const handleSubmitParameter = async () => {
    try {
      const nameParameter = form.nameParameter.trim();
      const valueParameter = form.valueParameter.trim();
      if (!nameParameter) {
        setValidationError("El nombre del parámetro es obligatorio.");
        return;
      }
      if (!valueParameter) {
        setValidationError("El valor del parámetro es obligatorio.");
        return;
      }
      setSaving(true);
      setValidationError("");
      const response = isCreate
        ? await parameterService.create({
            nameParameter,
            valueParameter,
          } as ParameterCreate)
        : await parameterService.update(
            selectedParameter!.IdParameter,
            {
              valueParameter,
            } as ParameterUpdate
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
            } el parámetro.`
        );
        return;
      }
      setParameterModalOpen(false);
      setSelectedParameter(null);
      setForm(emptyForm);
      await loadParameters();
      showResponseModal(
        "success",
        modalMode === "create"
          ? "Parámetro creado"
          : "Parámetro actualizado",
        response.Message ||
          `Parámetro ${
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
      setLoadingParameterId(null);
    }
  };

  useEffect(() => {
    loadParameters();
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
          <TuneOutlinedIcon sx={{ color: "#4B2E1F", fontSize: 30 }} />

          <Typography
            sx={{
              color: "#4B2E1F",
              fontSize: 26,
              fontWeight: 700,
            }}
          >
            Parámetros
          </Typography>
        </Stack>

        <Button
          variant="outlined"
          startIcon={<AddCircleOutlineOutlinedIcon />}
          onClick={openCreateModal}
          disabled={loading || saving}
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
          Crear parámetro
        </Button>
      </Stack>

      <Paper
        elevation={0}
        sx={{
          border: "1px solid #E0CDBB",
          borderRadius: 2,
          overflow: "hidden",
        }}
      >
        {loading ? (
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
                  ID
                </TableCell>

                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Nombre
                </TableCell>

                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Valor
                </TableCell>

                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Creado por
                </TableCell>

                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Fecha creación
                </TableCell>

                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Modificado por
                </TableCell>

                <TableCell sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                  Fecha modificación
                </TableCell>

                <TableCell
                  align="center"
                  sx={{ fontWeight: 700, color: "#4B2E1F" }}
                />
              </TableRow>
            </TableHead>

            <TableBody>
              {parameters.map((item) => {
                const isLoadingThisRow =
                  loadingParameterId === item.IdParameter;

                return (
                  <TableRow key={item.IdParameter} hover>
                    <TableCell>{item.IdParameter}</TableCell>

                    <TableCell>{item.nameParameter}</TableCell>

                    <TableCell>{item.valueParameter}</TableCell>

                    <TableCell>{item.createdByParameter}</TableCell>

                    <TableCell>
                      {formatDate(item.createdAtParameter)}
                    </TableCell>

                    <TableCell>
                      {item.updatedByParameter ?? "Sin modificación"}
                    </TableCell>

                    <TableCell>
                      {formatDate(item.updatedAtParameter)}
                    </TableCell>

                    <TableCell align="center">
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={
                          isLoadingThisRow ? (
                            <CircularProgress size={16} />
                          ) : (
                            <EditOutlinedIcon />
                          )
                        }
                        onClick={() => openUpdateModal(item)}
                        disabled={saving || loadingParameterId !== null}
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
                        {isLoadingThisRow ? "Cargando..." : "Actualizar"}
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}

              {parameters.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    No hay parámetros para mostrar.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </Paper>

      <Dialog
        open={parameterModalOpen}
        onClose={saving ? undefined : closeParameterModal}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            color: "#4B2E1F",
            fontWeight: 700,
          }}
        >
          {isCreate ? <AddCircleOutlineOutlinedIcon /> : <EditOutlinedIcon />}
          {isCreate ? "Crear parámetro" : "Actualizar parámetro"}
        </DialogTitle>

        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <Typography sx={{ color: "#6B4A3A", fontSize: 14 }}>
              {isCreate
                ? "Completa la información para crear un nuevo parámetro."
                : "Modifica la información del parámetro seleccionado."}
            </Typography>

            {validationError && (
              <Alert severity="warning">{validationError}</Alert>
            )}

            <TextField
              label="Nombre del parámetro"
              value={form.nameParameter}
              disabled={saving || !isCreate}
              fullWidth
              required
              helperText={!isCreate ? "El nombre del parámetro no se puede modificar." : ""}
              onChange={(event) =>
                setForm((prev) => ({
                  ...prev,
                  nameParameter: event.target.value,
                }))
              }
            />

            <TextField
              label="Valor del parámetro"
              value={form.valueParameter}
              disabled={saving}
              fullWidth
              required
              multiline
              minRows={3}
              onChange={(event) =>
                setForm((prev) => ({
                  ...prev,
                  valueParameter: event.target.value,
                }))
              }
            />
          </Stack>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            variant="outlined"
            startIcon={<CloseOutlinedIcon />}
            onClick={closeParameterModal}
            disabled={saving}
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
            Cancelar
          </Button>

          <Button
            variant="contained"
            startIcon={<SaveOutlinedIcon />}
            onClick={handleSubmitParameter}
            disabled={saving}
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