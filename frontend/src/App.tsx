import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { RequirePermission } from "./components/RequirePermission";
import { ApplicationUserPage } from "./pages/ApplicationUserPage";
import { DomiciliaryPage } from "./pages/DomiciliaryPage";
import { PublicRoute } from "./components/PublicRoute";
import { RequireAuth } from "./components/RequireAuth";
import { PointSalePage } from "./pages/PointSalePage";
import { ParameterPage } from "./pages/ParameterPage";
import { AppLayout } from "./components/AppLayout";
import { LoginPage } from "./pages/LoginPage";
import { HomePage } from "./pages/HomePage";
import { RolePage } from "./pages/RolePage";

function EmptyPage({ title }: { title: string }) {
  return <h2>{title}</h2>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={ <PublicRoute> <LoginPage /> </PublicRoute> }/>
        <Route element={<RequireAuth />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/maestros/punto-venta" element={ <RequirePermission path="/maestros/punto-venta"> <PointSalePage /> </RequirePermission> }/>
            <Route path="/maestros/domiciliarios" element={ <RequirePermission path="/maestros/domiciliarios"> <DomiciliaryPage /> </RequirePermission> }/>
            <Route path="/maestros/parametros" element={ <RequirePermission path="/maestros/parametros"> <ParameterPage /> </RequirePermission> }/>
            <Route path="/maestros/roles" element={ <RequirePermission path="/maestros/roles"> <RolePage /> </RequirePermission> }/>
            <Route path="/maestros/usuarios" element={ <RequirePermission path="/maestros/usuarios"> <ApplicationUserPage /> </RequirePermission> }/>
            <Route path="/registro-domicilios" element={ <RequirePermission path="/registro-domicilios"> <EmptyPage title="Registro de domicilios" /> </RequirePermission> }/>
            <Route path="/reporte-domicilios" element={ <RequirePermission path="/reporte-domicilios"> <EmptyPage title="Reporte de domicilios" /> </RequirePermission> }/>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}