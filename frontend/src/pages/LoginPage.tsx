import { Alert, Box, Button, CircularProgress, InputAdornment, Paper, Stack, TextField, Typography, } from "@mui/material";
import PersonOutlineOutlinedIcon from "@mui/icons-material/PersonOutlineOutlined";
import MarkEmailReadOutlinedIcon from "@mui/icons-material/MarkEmailReadOutlined";
import LoginOutlinedIcon from "@mui/icons-material/LoginOutlined";
import EmailOutlinedIcon from "@mui/icons-material/EmailOutlined";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import PinOutlinedIcon from "@mui/icons-material/PinOutlined";
import { getErrorMessage } from "../services/errorService";
import CoffeeIcon from "@mui/icons-material/Coffee";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

type LoginMode = "intranet" | "pointSale";

export function LoginPage() {
  const [loginMode, setLoginMode] = useState<LoginMode>("intranet");
  const [validationError, setValidationError] = useState("");
  const [pointSaleEmail, setPointSaleEmail] = useState("");
  const [pointSaleCode, setPointSaleCode] = useState("");
  const [codeWasSent, setCodeWasSent] = useState(false);
  const [infoMessage, setInfoMessage] = useState("");
  const [loading, setLoading] = useState(false);  
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");  

  const navigate = useNavigate();

  const {
    login,
    requestPointSaleCode,
    loginWithPointSaleCode,
  } = useAuth();

  const resetMessages = () => {
    setValidationError("");
    setInfoMessage("");
  };

  const handleChangeMode = (mode: LoginMode) => {
    setLoginMode(mode);
    resetMessages();
    setCodeWasSent(false);
    setPointSaleCode("");
  };

  const handleLogin = async () => {
    try {
      const cleanUsername = username.trim();

      if (!cleanUsername) {
        setValidationError("El usuario es obligatorio.");
        return;
      }

      if (!password) {
        setValidationError("La contraseña es obligatoria.");
        return;
      }

      setLoading(true);
      resetMessages();

      await login({
        username: cleanUsername,
        password,
      });

      navigate("/", { replace: true });
    } catch (err) {
      setValidationError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleRequestPointSaleCode = async () => {
    try {
      const cleanEmail = pointSaleEmail.trim().toLowerCase();

      if (!cleanEmail) {
        setValidationError("El correo del punto de venta es obligatorio.");
        return;
      }

      setLoading(true);
      resetMessages();

      await requestPointSaleCode(cleanEmail);

      setCodeWasSent(true);
      setInfoMessage("Te enviamos un código de 6 dígitos al correo del punto de venta.");
    } catch (err) {
      setValidationError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleLoginWithPointSaleCode = async () => {
    try {
      const cleanEmail = pointSaleEmail.trim().toLowerCase();
      const cleanCode = pointSaleCode.trim();

      if (!cleanEmail) {
        setValidationError("El correo del punto de venta es obligatorio.");
        return;
      }

      if (!cleanCode) {
        setValidationError("El código es obligatorio.");
        return;
      }

      if (!/^\d{6}$/.test(cleanCode)) {
        setValidationError("El código debe tener 6 dígitos.");
        return;
      }

      setLoading(true);
      resetMessages();

      await loginWithPointSaleCode(cleanEmail, cleanCode);

      navigate("/", { replace: true });
    } catch (err) {
      setValidationError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handlePointSaleCodeChange = (value: string) => {
    setPointSaleCode(value.replace(/\D/g, "").slice(0, 6));
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "#FFFDF8",
        display: "grid",
        placeItems: "center",
        px: 2,
      }}
    >
      <Paper
        elevation={0}
        sx={{
          width: "100%",
          maxWidth: 460,
          border: "1px solid #E0CDBB",
          borderRadius: 4,
          overflow: "hidden",
        }}
      >
        <Box
          sx={{
            bgcolor: "#4B2E1F",
            color: "#F7E8D8",
            px: 4,
            py: 4,
            textAlign: "center",
          }}
        >
          <Box
            component="img"
            src="/images/MonedaCrepes.png"
            alt="Crepes & Waffles"
            sx={{
              width: 110,
              height: 110,
              objectFit: "contain",
              mb: 2,
            }}
          />

          <Stack
            direction="row"
            spacing={1.2}
            sx={{
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <CoffeeIcon sx={{ fontSize: 32 }} />

            <Typography sx={{ fontSize: 21, fontWeight: 800 }}>
              Registro de domicilios
            </Typography>
          </Stack>

          <Typography sx={{ mt: 1, fontSize: 14, color: "#EAD9C9" }}>
            Inicia sesión con tu usuario de intranet o correo de punto de venta.
          </Typography>
        </Box>

        <Stack spacing={2.5} sx={{ px: 4, py: 4 }}>
          <Stack direction="row" spacing={1}>
            <Button
              fullWidth
              variant={loginMode === "intranet" ? "contained" : "outlined"}
              disabled={loading}
              onClick={() => handleChangeMode("intranet")}
              sx={{
                textTransform: "none",
                fontWeight: 700,
                bgcolor: loginMode === "intranet" ? "#4B2E1F" : "transparent",
                color: loginMode === "intranet" ? "#FFFFFF" : "#4B2E1F",
                borderColor: "#4B2E1F",
                "&:hover": {
                  bgcolor: loginMode === "intranet" ? "#3A2318" : "#FFF8EF",
                  borderColor: "#4B2E1F",
                },
              }}
            >
              Intranet
            </Button>

            <Button
              fullWidth
              variant={loginMode === "pointSale" ? "contained" : "outlined"}
              disabled={loading}
              onClick={() => handleChangeMode("pointSale")}
              sx={{
                textTransform: "none",
                fontWeight: 700,
                bgcolor: loginMode === "pointSale" ? "#4B2E1F" : "transparent",
                color: loginMode === "pointSale" ? "#FFFFFF" : "#4B2E1F",
                borderColor: "#4B2E1F",
                "&:hover": {
                  bgcolor: loginMode === "pointSale" ? "#3A2318" : "#FFF8EF",
                  borderColor: "#4B2E1F",
                },
              }}
            >
              Punto de venta
            </Button>
          </Stack>

          {validationError && (
            <Alert severity="warning">{validationError}</Alert>
          )}

          {infoMessage && (
            <Alert severity="success">{infoMessage}</Alert>
          )}

          {loginMode === "intranet" && (
            <>
              <TextField
                label="Usuario o correo"
                value={username}
                disabled={loading}
                fullWidth
                autoFocus
                onChange={(event) => setUsername(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    handleLogin();
                  }
                }}
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <PersonOutlineOutlinedIcon sx={{ color: "#8B6A55" }} />
                      </InputAdornment>
                    ),
                  },
                }}
              />

              <TextField
                label="Contraseña"
                type="password"
                value={password}
                disabled={loading}
                fullWidth
                onChange={(event) => setPassword(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    handleLogin();
                  }
                }}
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <LockOutlinedIcon sx={{ color: "#8B6A55" }} />
                      </InputAdornment>
                    ),
                  },
                }}
              />

              <Button
                variant="contained"
                startIcon={
                  loading ? (
                    <CircularProgress size={18} sx={{ color: "#FFFFFF" }} />
                  ) : (
                    <LoginOutlinedIcon />
                  )
                }
                onClick={handleLogin}
                disabled={loading}
                sx={{
                  bgcolor: "#4B2E1F",
                  color: "#FFFFFF",
                  height: 48,
                  textTransform: "none",
                  fontWeight: 700,
                  "&:hover": {
                    bgcolor: "#3A2318",
                  },
                }}
              >
                {loading ? "Ingresando..." : "Iniciar sesión"}
              </Button>
            </>
          )}

          {loginMode === "pointSale" && (
            <>
              <TextField
                label="Correo del punto de venta"
                type="email"
                value={pointSaleEmail}
                disabled={loading || codeWasSent}
                fullWidth
                autoFocus
                onChange={(event) => setPointSaleEmail(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !codeWasSent) {
                    handleRequestPointSaleCode();
                  }
                }}
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

              {codeWasSent && (
                <TextField
                  label="Código de 6 dígitos"
                  value={pointSaleCode}
                  disabled={loading}
                  fullWidth
                  onChange={(event) =>
                    handlePointSaleCodeChange(event.target.value)
                  }
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      handleLoginWithPointSaleCode();
                    }
                  }}
                  slotProps={{
                    htmlInput: {
                      maxLength: 6,
                      inputMode: "numeric",
                      pattern: "[0-9]*",
                    },
                    input: {
                      startAdornment: (
                        <InputAdornment position="start">
                          <PinOutlinedIcon sx={{ color: "#8B6A55" }} />
                        </InputAdornment>
                      ),
                    },
                  }}
                />
              )}

              {!codeWasSent ? (
                <Button
                  variant="contained"
                  startIcon={
                    loading ? (
                      <CircularProgress size={18} sx={{ color: "#FFFFFF" }} />
                    ) : (
                      <MarkEmailReadOutlinedIcon />
                    )
                  }
                  onClick={handleRequestPointSaleCode}
                  disabled={loading}
                  sx={{
                    bgcolor: "#4B2E1F",
                    color: "#FFFFFF",
                    height: 48,
                    textTransform: "none",
                    fontWeight: 700,
                    "&:hover": {
                      bgcolor: "#3A2318",
                    },
                  }}
                >
                  {loading ? "Enviando código..." : "Enviar código"}
                </Button>
              ) : (
                <Stack spacing={1.5}>
                  <Button
                    variant="contained"
                    startIcon={
                      loading ? (
                        <CircularProgress size={18} sx={{ color: "#FFFFFF" }} />
                      ) : (
                        <LoginOutlinedIcon />
                      )
                    }
                    onClick={handleLoginWithPointSaleCode}
                    disabled={loading}
                    sx={{
                      bgcolor: "#4B2E1F",
                      color: "#FFFFFF",
                      height: 48,
                      textTransform: "none",
                      fontWeight: 700,
                      "&:hover": {
                        bgcolor: "#3A2318",
                      },
                    }}
                  >
                    {loading ? "Validando..." : "Ingresar con código"}
                  </Button>

                  <Button
                    variant="text"
                    disabled={loading}
                    onClick={() => {
                      setCodeWasSent(false);
                      setPointSaleCode("");
                      resetMessages();
                    }}
                    sx={{
                      color: "#4B2E1F",
                      textTransform: "none",
                      fontWeight: 700,
                    }}
                  >
                    Cambiar correo
                  </Button>
                </Stack>
              )}
            </>
          )}
        </Stack>
      </Paper>
    </Box>
  );
}