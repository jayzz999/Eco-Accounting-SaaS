import Link from 'next/link'
import { ArrowRight, Leaf, BarChart3, FileText, Shield } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Leaf className="h-8 w-8 text-green-600" />
            <span className="text-2xl font-bold text-gray-900">EcoAccounting</span>
          </div>
          <div className="flex gap-4">
            <Link
              href="/dashboard"
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 transition-colors"
            >
              Dashboard
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="mx-auto max-w-3xl">
          <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl">
            AI-Powered Environmental Reporting
          </h1>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Automate your ESG compliance, carbon footprint tracking, and GRI report generation
            with cutting-edge AI technology. Upload bills, get instant insights.
          </p>
          <div className="mt-10 flex items-center justify-center gap-6">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-lg font-semibold text-white hover:bg-blue-700 transition-colors"
            >
              Get Started
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="#features"
              className="text-lg font-semibold text-gray-900 hover:text-gray-700"
            >
              Learn more
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900">
            Everything you need for ESG reporting
          </h2>
          <p className="mt-4 text-lg text-gray-600">
            Comprehensive environmental accounting platform built for the modern enterprise
          </p>
        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <Leaf className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">AI Bill Processing</h3>
            <p className="mt-2 text-gray-600">
              Automatically extract data from utility bills using AWS Textract and Claude AI
            </p>
          </div>

          <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
              <BarChart3 className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">Carbon Tracking</h3>
            <p className="mt-2 text-gray-600">
              Real-time carbon footprint calculation with location-specific emission factors
            </p>
          </div>

          <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100">
              <FileText className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">GRI Reports</h3>
            <p className="mt-2 text-gray-600">
              Generate compliant GRI 302, 303, and 305 reports with one click
            </p>
          </div>

          <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-red-100">
              <Shield className="h-6 w-6 text-red-600" />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">Compliance</h3>
            <p className="mt-2 text-gray-600">
              Automated compliance checking against regional environmental regulations
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-blue-600 py-20">
        <div className="container mx-auto px-4">
          <div className="grid gap-8 md:grid-cols-3 text-center text-white">
            <div>
              <div className="text-4xl font-bold">100%</div>
              <div className="mt-2 text-blue-100">Automated Processing</div>
            </div>
            <div>
              <div className="text-4xl font-bold">3+</div>
              <div className="mt-2 text-blue-100">Reporting Frameworks</div>
            </div>
            <div>
              <div className="text-4xl font-bold">AWS</div>
              <div className="mt-2 text-blue-100">Cloud-Native Architecture</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="mx-auto max-w-2xl">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900">
            Ready to automate your environmental reporting?
          </h2>
          <p className="mt-4 text-lg text-gray-600">
            Join organizations leveraging AI for ESG compliance
          </p>
          <div className="mt-8">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-lg font-semibold text-white hover:bg-blue-700 transition-colors"
            >
              Start Free Trial
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-gray-50 py-12">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Leaf className="h-6 w-6 text-green-600" />
              <span className="text-lg font-semibold text-gray-900">EcoAccounting</span>
            </div>
            <p className="text-sm text-gray-600">
              © 2024 EcoAccounting SaaS. Built for Operisoft.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
