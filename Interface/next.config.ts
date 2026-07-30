import type { NextConfig } from 'next';
import os from 'os';

// Helper function to dynamically discover the host machine's local Wi-Fi / Ethernet IP
function getLocalNetworkIP(): string | null {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    const networkInterface = interfaces[name];
    if (!networkInterface) continue;

    for (const net of networkInterface) {
      // Look for IPv4 addresses that are NOT loopback (localhost)
      if (net.family === 'IPv4' && !net.internal) {
        return net.address;
      }
    }
  }
  return null;
}

const localIP = getLocalNetworkIP();
const PORT = process.env.PORT || '3000'; // Default Next.js port

// Construct the allowed origins array dynamically
const dynamicOrigins = ['localhost', `127.0.0.1:${PORT}`];
if (localIP) {
  dynamicOrigins.push(`${localIP}:${PORT}`);
  // Add a version without the port if needed for specific cross-origin strictness
  dynamicOrigins.push(localIP); 
}

console.log('🚀 Dynamic Allowed Origins Configured:', dynamicOrigins);

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      // Binds Server Actions security dynamically to your current Wi-Fi/Network IP
      allowedOrigins: dynamicOrigins,
    },
  },
  // Allows hot-reloading and dev tools to pass through the Wi-Fi IP securely
  allowedDevOrigins: dynamicOrigins,
};

export default nextConfig;
