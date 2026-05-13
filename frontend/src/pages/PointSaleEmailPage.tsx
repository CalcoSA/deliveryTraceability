import { Alert, Box, Button, Chip, CircularProgress, Dialog, DialogActions, DialogContent, DialogTitle, IconButton, Paper, Stack, Switch, Table, TableBody, TableCell, TableHead, TableRow, TextField, Tooltip, Typography, InputAdornment } from "@mui/material";
import type { PointSaleEmail, PointSaleEmailCreate, PointSaleEmailUpdate, } from "../models/PointSaleEmail";
import { pointSaleEmailService } from "../services/pointSaleEmailService";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import EmailOutlinedIcon from "@mui/icons-material/EmailOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { getErrorMessage } from "../services/errorService";
import { useEffect, useMemo, useState } from "react";

interface PointSaleEmailFormState {
  IdPointSaleEmail: number | null;
  emailPointSale: string;
  statusPointSaleEmail: boolean;
}

const initialForm: PointSaleEmailFormState = {
  IdPointSaleEmail: null,
  emailPointSale: "",
  statusPointSaleEmail: true,
};

export function PointSaleEmailPage() {
  const [form, setForm] = useState<PointSaleEmailFormState>(initialForm);
  const [emails, setEmails] = useState<PointSaleEmail[]>([]);
  const [validationError, setValidationError] = useState("");
  const [openDialog, setOpenDialog] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const isEditing = useMemo(() => form.IdPointSaleEmail !== null, [form.IdPointSaleEmail]);

  const loadEmails = async () => {
    try {
      setLoading(true);
      setError("");
      setMessage("");

      const response = await pointSaleEmailService.getAll();

      setEmails(response.result ?? []);
    } catch (err) {
      setEmails([]);
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const openCreateDialog = () => {
    setForm(initialForm);
    setValidationError("");
    setOpenDialog(true);
  };

  const openEditDialog = (item: PointSaleEmail) => {
    setForm({
      IdPointSaleEmail: item.IdPointSaleEmail,
      emailPointSale: item.emailPointSale,
      statusPointSaleEmail: item.statusPointSaleEmail,
    });

    setValidationError("");
    setOpenDialog(true);
  };

  const closeDialog = () => {
    if (saving) return;

    setOpenDialog(false);
    setForm(initialForm);
    setValidationError("");
  };

  const validateForm = () => {
    const email = form.emailPointSale.trim().toLowerCase();

    if (!email) {
      return "El correo del punto de venta es obligatorio.";
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return "Debes ingresar un correo válido.";
    }

    return "";
  };

  const handleSave = async () => {
    try {
      const validation = validateForm();

      if (validation) {
        setValidationError(validation);
        return;
      }

      setSaving(true);
      setValidationError("");
      setError("");
      setMessage("");

      const cleanEmail = form.emailPointSale.trim().toLowerCase();

      if (form.IdPointSaleEmail === null) {
        const payload: PointSaleEmailCreate = {
          emailPointSale: cleanEmail,
        };

        await pointSaleEmailService.create(payload);

        setMessage("Correo de punto de venta creado correctamente.");
      } else {
        const payload: PointSaleEmailUpdate = {
          emailPointSale: cleanEmail,
          statusPointSaleEmail: form.statusPointSaleEmail,
        };

        await pointSaleEmailService.update(form.IdPointSaleEmail, payload);

        setMessage("Correo de punto de venta actualizado correctamente.");
      }

      setOpenDialog(false);
      setForm(initialForm);
      await loadEmails();
    } catch (err) {
      setValidationError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const handleToggleStatus = async (item: PointSaleEmail) => {
    try {
      setSaving(true);
      setError("");
      setMessage("");

      await pointSaleEmailService.update(item.IdPointSaleEmail, {
        statusPointSaleEmail: !item.statusPointSaleEmail,
      });

      setMessage(
        !item.statusPointSaleEmail
          ? "Correo activado correctamente."
          : "Correo inactivado correctamente."
      );

      await loadEmails();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    loadEmails();
  }, []);

  return (
    <Box>
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={2}
        sx={{
          justifyContent: "space-between",
          alignItems: { xs: "stretch", md: "center" },
          mb: 2,
        }}
      >
        <Box>
          <Typography sx={{ fontSize: 22, fontWeight: 800, color: "#4B2E1F" }}>
            Correos de punto de venta
          </Typography>

          <Typography sx={{ fontSize: 14, color: "#8B6A55", mt: 0.5 }}>
            Administra los correos autorizados para ingresar con código de verificación.
          </Typography>
        </Box>

        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<RefreshOutlinedIcon />}
            disabled={loading || saving}
            onClick={loadEmails}
            sx={{
              borderColor: "#4B2E1F",
              color: "#4B2E1F",
              textTransform: "none",
              fontWeight: 700,
            }}
          >
            Actualizar
          </Button>

          <Button
            variant="contained"
            startIcon={<AddOutlinedIcon />}
            disabled={loading || saving}
            onClick={openCreateDialog}
            sx={{
              bgcolor: "#4B2E1F",
              color: "#FFFFFF",
              textTransform: "none",
              fontWeight: 700,
              "&:hover": {
                bgcolor: "#3A2318",
              },
            }}
          >
            Nuevo correo
          </Button>
        </Stack>
      </Stack>

      {message && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper
        elevation={0}
        sx={{
          border: "1px solid #E0CDBB",
          borderRadius: 3,
          overflow: "hidden",
        }}
      >
        {loading ? (
          <Stack spacing={2} sx={{ alignItems: "center", py: 6 }}>
            <CircularProgress sx={{ color: "#4B2E1F" }} />
            <Typography sx={{ color: "#8B6A55" }}>
              Cargando correos de punto de venta...
            </Typography>
          </Stack>
        ) : (
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: "#FFF8EF" }}>
                <TableCell sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                  Correo
                </TableCell>

                <TableCell sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                  Estado
                </TableCell>

                <TableCell sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                  Creado
                </TableCell>

                <TableCell align="right" sx={{ fontWeight: 800, color: "#4B2E1F" }}>
                  Acciones
                </TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {emails.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4}>
                    <Stack sx={{ alignItems: "center", py: 5 }}>
                      <EmailOutlinedIcon sx={{ fontSize: 42, color: "#8B6A55", mb: 1 }} />
                      <Typography sx={{ color: "#8B6A55" }}>
                        No hay correos de punto de venta registrados.
                      </Typography>
                    </Stack>
                  </TableCell>
                </TableRow>
              ) : (
                emails.map((item) => (
                  <TableRow key={item.IdPointSaleEmail} hover>
                    <TableCell>
                      <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
                        <EmailOutlinedIcon sx={{ color: "#8B6A55" }} />
                        <Typography sx={{ fontWeight: 700, color: "#4B2E1F" }}>
                          {item.emailPointSale}
                        </Typography>
                      </Stack>
                    </TableCell>

                    <TableCell>
                      <Chip
                        label={item.statusPointSaleEmail ? "Activo" : "Inactivo"}
                        size="small"
                        sx={{
                          fontWeight: 700,
                          bgcolor: item.statusPointSaleEmail ? "#E8F5E9" : "#FFEBEE",
                          color: item.statusPointSaleEmail ? "#2E7D32" : "#C62828",
                        }}
                      />
                    </TableCell>

                    <TableCell>
                      {new Date(item.createdAtPointSaleEmail).toLocaleString("es-CO")}
                    </TableCell>

                    <TableCell align="right">
                      <Tooltip title={item.statusPointSaleEmail ? "Inactivar" : "Activar"}>
                        <span>
                          <Switch
                            checked={item.statusPointSaleEmail}
                            disabled={saving}
                            onChange={() => handleToggleStatus(item)}
                          />
                        </span>
                      </Tooltip>

                      <Tooltip title="Editar correo">
                        <span>
                          <IconButton
                            disabled={saving}
                            onClick={() => openEditDialog(item)}
                            sx={{ color: "#4B2E1F" }}
                          >
                            <EditOutlinedIcon />
                          </IconButton>
                        </span>
                      </Tooltip>

                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        )}
      </Paper>

      <Dialog open={openDialog} onClose={closeDialog} fullWidth maxWidth="sm">
        <DialogTitle sx={{ fontWeight: 800, color: "#4B2E1F" }}>
          {isEditing ? "Editar correo de punto de venta" : "Nuevo correo de punto de venta"}
        </DialogTitle>

        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            {validationError && (
              <Alert severity="warning">{validationError}</Alert>
            )}

            <TextField
              label="Correo del punto de venta"
              type="email"
              value={form.emailPointSale}
              disabled={saving}
              fullWidth
              autoFocus
              onChange={(event) =>
                setForm((prev) => ({
                  ...prev,
                  emailPointSale: event.target.value,
                }))
              }
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailOutlinedIcon sx={{ color: "#8B6A55" }} />
                    </InputAdornment>
                  ),
                },
              }}
            />

            {isEditing && (
              <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
                <Switch
                  checked={form.statusPointSaleEmail}
                  disabled={saving}
                  onChange={(event) =>
                    setForm((prev) => ({
                      ...prev,
                      statusPointSaleEmail: event.target.checked,
                    }))
                  }
                />

                <Typography sx={{ color: "#4B2E1F", fontWeight: 700 }}>
                  {form.statusPointSaleEmail ? "Activo" : "Inactivo"}
                </Typography>
              </Stack>
            )}
          </Stack>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button
            onClick={closeDialog}
            disabled={saving}
            sx={{
              color: "#4B2E1F",
              textTransform: "none",
              fontWeight: 700,
            }}
          >
            Cancelar
          </Button>

          <Button
            variant="contained"
            onClick={handleSave}
            disabled={saving}
            sx={{
              bgcolor: "#4B2E1F",
              color: "#FFFFFF",
              textTransform: "none",
              fontWeight: 700,
              "&:hover": {
                bgcolor: "#3A2318",
              },
            }}
          >
            {saving ? "Guardando..." : "Guardar"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}