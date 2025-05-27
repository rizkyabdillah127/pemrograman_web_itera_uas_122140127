import React from "react";
import { Button } from "../ui/button";
import { Link } from "react-router-dom";

export default function ApcerHeroSection() {
  return (
    <section className="bg-gradient-to-br pt-20">
      <div className="max-w-7xl mx-auto px-6 md:px-12 lg:px-20">
        {/* Header Section */}
        <div className="flex flex-col lg:flex-row items-center justify-between gap-12 mb-20">
          {/* Left Column: Text & Call to Action */}
          <div className="lg:w-1/2 text-center lg:text-left">
            <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 leading-tight mb-4 drop-shadow-sm">
              Apa Cerita?
            </h1>
            {/* Sub-judul menggunakan warna primary (stone) */}
            <h2 className="text-4xl md:text-5xl font-bold text-primary mb-6 drop-shadow-sm">
              Ruang Anonim untuk Berbagi Kisahmu
            </h2>
            <p className="text-xl text-gray-700 max-w-xl lg:max-w-none mx-auto lg:mx-0 mb-8 leading-relaxed">
              Apcer adalah tempat di mana setiap suara didengar, setiap
              pengalaman berharga. Berbagi tanpa beban identitas, terhubung
              melalui cerita.
            </p>
            <Link to={"/register"}>
              {/* Tombol dengan latar belakang primary (stone) dan teks primary-foreground (light) */}
              <Button className="inline-flex items-center justify-center bg-primary hover:bg-primary/90 text-primary-foreground font-bold py-3 px-8 rounded-full shadow-xl transition-all duration-300 transform hover:scale-105 hover:shadow-2xl">
                Mulai Bercerita Sekarang
              </Button>
            </Link>
          </div>

          {/* Right Column: Visual Element Placeholder */}
          <div className="lg:w-1/2 flex justify-center items-center">
            {/* Lingkaran dengan latar belakang secondary (off-white) */}
            <div className="relative w-64 h-64 md:w-80 md:h-80 bg-secondary rounded-full flex items-center justify-center p-8 shadow-inner transform rotate-6 animate-pulse-slow">
              {/* Teks di dalam lingkaran dengan warna primary (stone) */}
              <p className="text-primary text-lg font-semibold text-center">
                Cerita Anda
                <br />
                Menanti untuk Dibagikan
              </p>
              {/* Bentuk-bentuk abstrak menggunakan primary dengan opacity */}
              <div className="absolute -top-4 -left-4 w-16 h-16 bg-primary/[0.1] rounded-xl opacity-60 transform rotate-12"></div>
              <div className="absolute -bottom-8 -right-8 w-24 h-24 bg-primary/[0.2] rounded-full opacity-60 transform -rotate-12"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
