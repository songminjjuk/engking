import React, { useEffect, useRef } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const PrivateRoute = ({ element, isLoggedIn }) => {
  const location = useLocation();
  const alertShownRef = useRef(false);

  useEffect(() => {
    if (!isLoggedIn && !alertShownRef.current) {
      alert('로그인 후 사용하실 수 있습니다 !');
      alertShownRef.current = true;
    }
  }, [isLoggedIn]);

  if (!isLoggedIn) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return element;
};

export default PrivateRoute;
