
async function search() {
    const query = document.getElementById('query').value;
    const category = document.getElementById('category').value;
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');

    console.log(`Query: ${query}`);
    console.log(`Category: ${category}`);

   
    loadingDiv.style.display = 'block'; 
    resultsDiv.innerHTML = ''; 

    try {
        const response = await axios.get(`http://localhost:7071/api/Saravananfinproject?query=${query}&department=${category}`);
        console.log('Response:', response);
        const results = response.data;

     
        loadingDiv.style.display = 'none';

        if (results && results.response) {
            const responseText = results.response;
            let documentsLinks = results.documents_links;

  
            let resultHtml = `<div class="response-text"><p></p></div>`;
            resultsDiv.innerHTML = resultHtml; 

            let responseContainer = resultsDiv.querySelector('.response-text p');
            let currentText = '';
            let index = 0;

           
            const typeResponse = () => {
                if (index < responseText.length) {
                    currentText += responseText.charAt(index);
                    responseContainer.textContent = currentText;
                    index++;
                } else {
                    clearInterval(typeInterval);
                    showDocumentLinks(); 
                }
            };

    
            const typeInterval = setInterval(typeResponse, 30); 

       
            let documentsHtml = '';

          
            const showDocumentLinks = () => {
              
                if (responseText === "No relevant content found.") {
                    documentsHtml = "";  
                } else if (documentsLinks && typeof documentsLinks === 'string' && documentsLinks.trim() !== '') {
                   
                    const documentLinks = documentsLinks.split('\n');

                    
                    let uniqueDocuments = new Set();

                    documentLinks.forEach(link => {
                        if (link.trim()) {
                    
                            if (link.includes("Here are some related documents for your reference:")) {
                                return;
                            }

                          
                            const [docLink, departmentInfo] = link.split(' (Department: ');

                            const department = departmentInfo ? departmentInfo.replace(')', '') : 'N/A';

                            
                            const actualDocLink = docLink.includes("https://acuvatehyd.sharepoint.com") ? docLink.split("https://acuvatehyd.sharepoint.com")[1] : docLink;
                            const finalDocLink = `https://acuvatehyd.sharepoint.com${actualDocLink}`;

                            const docName = finalDocLink.substring(finalDocLink.lastIndexOf("/") + 1);

                           
                            if (!uniqueDocuments.has(finalDocLink)) {
                                uniqueDocuments.add(finalDocLink);

                           
                                documentsHtml += `
                                    <div class="document">
                                        <p><strong>PDF Name:</strong> ${docName}</p>
                                        <a href="${finalDocLink.trim()}" target="_blank" class="download-button">Click to View Document</a>
                                    </div>
                                `;
                            }
                        }
                    });
                } else {
                  
                    documentsHtml = "<p>No documents found.</p>";
                }

              
                let documentLinksDiv = document.createElement('div');
                documentLinksDiv.innerHTML = documentsHtml;
                resultsDiv.appendChild(documentLinksDiv);
            };

        } else {
            resultsDiv.innerHTML = "<p>No results found.</p>";
        }
    } catch (error) {
        console.error('Error fetching data:', error);
        alert(`Error: ${error.message}`);
        
 
        loadingDiv.style.display = 'none';
    }
}
