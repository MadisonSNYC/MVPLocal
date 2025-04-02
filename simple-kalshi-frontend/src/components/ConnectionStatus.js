import React from 'react';

const ConnectionStatus = ({ connected, error }) => {
  if (connected) return null;
  
  return (
    <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="ml-3">
          <p className="text-sm font-medium">
            Backend connection failed. The application may not function correctly.
          </p>
          {error && (
            <p className="text-xs mt-1">
              Error: {error}
            </p>
          )}
          <p className="text-xs mt-2">
            Please check your backend server or go to Settings to configure the connection.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ConnectionStatus; 