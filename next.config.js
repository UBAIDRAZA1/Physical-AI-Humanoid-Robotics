/** @type {import('next').NextConfig} */
const nextConfig = {
  // Ye line sabse important hai
  basePath: "/physical-ai-book",
  assetPrefix: "/physical-ai-book/",
  
  // Agar images bhi 404 de rahe hain to ye bhi add kar do
  images: {
    unoptimized: true
  },

  trailingSlash: true, // optional, lekin Netlify par kaam aata hai
  output: "standalone", // optional, lekin chhote projects ke liye acha
}

module.exports = nextConfig