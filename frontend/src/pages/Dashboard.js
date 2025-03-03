import { useEffect, useState } from "react";
import axios from "axios";
import "../styles/dashboard.css";
import { Bar, Pie } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

function Dashboard() {
  const [previousSearches, setPreviousSearches] = useState([]);
  const [newKeyword, setNewKeyword] = useState("");
  const [error, setError] = useState("");
  const [chartData, setChartData] = useState(null);
  const [chartType, setChartType] = useState(null);

  useEffect(() => {
    axios.get("http://localhost:5012/api/previous-searches")
    .then((response) => {
      if (Array.isArray(response.data.keywords)) {
        setPreviousSearches(response.data.keywords);
      } else {
        setPreviousSearches([]);
      }
    })
    .catch((error) => {
      console.error("Error fetching previous searches:", error);
      setPreviousSearches([]);
    });
  }, []);

  const handleSearch = () => {
    if (!newKeyword.trim()) return;
    
    axios.post("http://localhost:5012/api/analyze", { keyword: newKeyword })
      .then((response) => {
        setPreviousSearches([...previousSearches, response.data.keyword]);
        setNewKeyword("");
        handleShowChart(response.data.keyword, "pie");
        handleShowChart(response.data.keyword, "bar");
      })
      .catch(() => setError("Error processing search"));
  };

  const handleShowChart = (keyword, type) => {
    axios.get(`http://localhost:5012/api/sentiment/${keyword}`)
      .then((response) => {
        setChartData({
          labels: ["Positive", "Negative", "Neutral"],
          datasets: [
            {
              label: "Sentiments",
              data: [
                response.data.positive_count,
                response.data.negative_count,
                response.data.neutral_count,
              ],
              backgroundColor: ["#4CAF50", "#F44336", "#FFEB3B"],
              borderColor: ["#388E3C", "#D32F2F", "#FBC02D"],
              borderWidth: 1,
            },
          ],
        });
        setChartType(type);
      })
      .catch(() => setError("Error fetching sentiment data"));
  };

  return (
    <div className="dashboard">
      <h2>Sentiment Analysis Dashboard</h2>
      
      {/* Display Previous Searches */}
      <div className="previous-searches-box">
        <h3>Previous Searches</h3>
        {previousSearches.length === 0 ? (
          <p>No previous searches found.</p>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Keyword</th>
                  <th>Pie Chart</th>
                  <th>Bar Chart</th>
                </tr>
              </thead>
              <tbody>
              {previousSearches.length > 0 ? (
                previousSearches.map((search, index) => (
                  <tr key={index}>
                    <td>{search}</td>
                    <td>
                      <button onClick={() => handleShowChart(search, "pie")}>Pie</button>
                    </td>
                    <td>
                      <button onClick={() => handleShowChart(search, "bar")}>Bar</button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="3">No previous searches available</td>
                </tr>
              )}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {/* Search for New Keywords */}
      <div className="search-section">
        <input 
          type="text" 
          placeholder="Search for a keyword..." 
          value={newKeyword} 
          onChange={(e) => setNewKeyword(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      
      {error && <p className="error-message">{error}</p>}
      
      {/* Display Chart */}
      {chartData && (
        <div className="chart-container">
          <h3>Sentiment Analysis</h3>
          {chartType === "bar" ? (
            <Bar data={chartData} options={{ responsive: true }} />
          ) : (
            <Pie data={chartData} options={{ responsive: true }} />
          )}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
