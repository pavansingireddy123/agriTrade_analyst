// import React from 'react';
// import FinancialOverview from '../components/dashboard/FinancialOverview';
// import LoanCalculator from '../components/dashboard/LoanCalculator';
// import { transactions, loanOptions, cropPlans } from '../data/mockData';
// const FinanceTracker = () => {
//   // Static financial data defined in parent component
//   const staticFinancialSummary = {
//     totalIncome: 100000,  // ₹12,50,000
//     totalExpense: 5000,   // ₹8,75,000
//     balance: 5000      // ₹3,75,000
//   };

//   return (
//     <div className="max-w-7xl mx-auto px-4 py-8">
//       <h1 className="text-3xl font-bold text-gray-900 mb-8">Financial Dashboard</h1>
      
//       <div className="space-y-8">
//         {/* Pass static data as prop */}
//         <FinancialOverview summary={staticFinancialSummary} />
        
//         <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
//           <LoanCalculator 
//             financialSummary={staticFinancialSummary}
//             loanOptions={loanOptions} // Add static loan options if needed
//           />
//         </div>
//       </div>
//     </div>
//   );
// };

// export default FinanceTracker;
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FinancialOverview from '../components/dashboard/FinancialOverview';
import LoanCalculator from '../components/dashboard/LoanCalculator';
import { loanOptions } from '../data/mockData';

const FinanceTracker = () => {
  const [formData, setFormData] = useState({
    district: '',
    crop: '',
    season: '',
    acres: '1'
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [options, setOptions] = useState({
    districts: [],
    crops: [],
    seasons: []
  });

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [districtsRes, cropsRes, seasonsRes] = await Promise.all([
          axios.get('http://localhost:5000/districts'),
          axios.get('http://localhost:5000/crops'),
          axios.get('http://localhost:5000/seasons')
        ]);
        
        setOptions({
          districts: districtsRes.data,
          crops: cropsRes.data,
          seasons: seasonsRes.data
        });
      } catch (err) {
        setError('Failed to load options. Please refresh the page.');
      }
    };
    
    fetchOptions();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:5000/calculate', {
        ...formData,
        acres: parseFloat(formData.acres)
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Calculation failed. Please check your inputs.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-4">Agricultural Profit Calculator</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-1">District:</label>
              <select
                name="district"
                value={formData.district}
                onChange={handleChange}
                required
                className="w-full p-2 border border-gray-300 rounded-md"
                disabled={loading}
              >
                <option value="">Select District</option>
                {options.districts.map(district => (
                  <option key={district} value={district}>{district}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-1">Crop:</label>
              <select
                name="crop"
                value={formData.crop}
                onChange={handleChange}
                required
                className="w-full p-2 border border-gray-300 rounded-md"
                disabled={loading}
              >
                <option value="">Select Crop</option>
                {options.crops.map(crop => (
                  <option key={crop} value={crop}>
                    {crop.charAt(0).toUpperCase() + crop.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-1">Season:</label>
              <select
                name="season"
                value={formData.season}
                onChange={handleChange}
                required
                className="w-full p-2 border border-gray-300 rounded-md"
                disabled={loading}
              >
                <option value="">Select Season</option>
                {options.seasons.map(season => (
                  <option key={season} value={season}>{season}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="block text-sm font-medium text-gray-700 mb-1">Acres:</label>
              <input
                type="number"
                name="acres"
                min="0.1"
                step="0.1"
                value={formData.acres}
                onChange={handleChange}
                required
                className="w-full p-2 border border-gray-300 rounded-md"
                disabled={loading}
              />
            </div>
          </div>

          <button
            type="submit"
            className={`w-full py-2 px-4 rounded-md text-white font-medium ${loading ? 'bg-gray-400' : 'bg-green-600 hover:bg-green-700'}`}
            disabled={loading}
          >
            {loading ? 'Calculating...' : 'Calculate'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}
      </div>

      {result && (
        <div className="space-y-8">
          <FinancialOverview summary={{
            totalIncome: result.totalIncome,
            totalExpense: result.totalExpense,
            balance: result.balance
          }} />
          
          <div style={{ display: 'flex', justifyContent: 'center' }} className="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full px-8 py-6" >
          
            <LoanCalculator 
              financialSummary={{
                totalIncome: result.totalIncome,
                totalExpense: result.totalExpense,
                balance: result.balance
              }}
              loanOptions={loanOptions}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default FinanceTracker;