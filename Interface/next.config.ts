import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};
//Jetson -> '10.42.0.124'
module.exports = {
    allowedDevOrigins: ['10.42.0.124','10.225.60.141']
}
export default nextConfig;
