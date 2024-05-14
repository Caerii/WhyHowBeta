'use client';

import {
  Box,
  ChakraProvider,
  Flex,
  Button,
  Text,
  VStack,
  useToast,
  Heading,
  theme,
  Icon,
  Input,
  Textarea,
  Checkbox,
  Stack,
  Badge,
  SimpleGrid
} from '@chakra-ui/react';
import { FaRocket, FaFileAlt, FaTrash } from 'react-icons/fa';
import axios from "axios";
import { useState, useEffect } from "react";

export default function Home() {
  const [message, setMessage] = useState("Awaiting response...");
  const [namespace, setNamespace] = useState("");
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState(null);
  const [importantPhrases, setImportantPhrases] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [useRawText, setUseRawText] = useState(false);
  const toast = useToast();

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get('http://localhost:8000/list_files');
      setDocuments(response.data.files || []);
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleNamespaceChange = (e) => {
    setNamespace(e.target.value);
  };

  const handleUpload = async () => {
    // Check if namespace and file are provided
    if (!namespace) {
      toast({
        title: "Error",
        description: "Namespace is required.",
        status: "error",
        duration: 9000,
        isClosable: true,
      });
      return;
    }

    if (!file) {
      toast({
        title: "Error",
        description: "File is required.",
        status: "error",
        duration: 9000,
        isClosable: true,
      });
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("namespace", namespace);

      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const { filename, namespace } = response.data;

      toast({
        title: "Success",
        description: "Document uploaded successfully.",
        status: "success",
        duration: 9000,
        isClosable: true,
      });

      // You may want to update your state or call a function to refresh the document list
      fetchDocuments();

    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to upload document: ${error.message}`,
        status: "error",
        duration: 9000,
        isClosable: true,
      });
    }
  };


  const handleQuery = async () => {
    try {
      const response = await axios.post('http://localhost:8000/query', {
        namespace: namespace,
        question: question
      });
      setMessage(response.data.response.answer);
      toast({
        title: "Success",
        description: "Query successful.",
        status: "success",
        duration: 9000,
        isClosable: true,
      });
    } catch (error) {
      setMessage(`An error occurred: ${error.message}`);
      toast({
        title: "Error",
        description: `Failed to query graph: ${error.message}`,
        status: "error",
        duration: 9000,
        isClosable: true,
      });
    }
  };

  const handleDelete = async (docName) => {
  try {
    const formData = new FormData();
    formData.append('file_name', docName);

    const response = await axios.post('http://localhost:8000/delete_file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    toast({
      title: "Success",
      description: `Document ${docName} deleted successfully.`,
      status: "success",
      duration: 9000,
      isClosable: true,
    });
    fetchDocuments();
  } catch (error) {
    console.error("Error deleting document:", error);
    toast({
      title: "Error",
      description: `Failed to delete document: ${error.message}`,
      status: "error",
      duration: 9000,
      isClosable: true,
    });
  }
};


  const toggleDocumentSelection = (docName) => {
    setSelectedDocs(prevSelectedDocs => {
      if (prevSelectedDocs.includes(docName)) {
        return prevSelectedDocs.filter(doc => doc !== docName);
      } else if (prevSelectedDocs.length < 3) {
        return [...prevSelectedDocs, docName];
      } else {
        return prevSelectedDocs;
      }
    });
  };

  const isDocumentSelected = (docName) => selectedDocs.includes(docName);

  const handleCreateGraph = async () => {
    if (selectedDocs.length === 0) {
      toast({
        title: "Error",
        description: "Please select at least one document to create a graph.",
        status: "error",
        duration: 9000,
        isClosable: true,
      });
      return;
    }
  
    try {
      const response = await axios.post('http://localhost:8000/create_graph', {
        namespace: namespace,
        files: selectedDocs,
        use_raw_text: useRawText
      });
  
      const { important_phrases, questions, extracted_graph } = response.data;
  
      setImportantPhrases(important_phrases || []);
      setQuestions(questions || []);
      setMessage("Graph created successfully.");
      toast({
        title: "Success",
        description: "Graph created successfully.",
        status: "success",
        duration: 9000,
        isClosable: true,
      });
  
    } catch (error) {
      setMessage(`An error occurred: ${error.message}`);
      toast({
        title: "Error",
        description: `Failed to create graph: ${error.message}`,
        status: "error",
        duration: 9000,
        isClosable: true,
      });
    }
  };
  

  return (
    <ChakraProvider>
      <Flex minHeight="100vh" align="center" justifyContent="center" bg={theme.colors.gray[50]}>
        <VStack spacing={5} p={8} boxShadow="md" borderRadius="lg" bg="white" width="80%">
          <Icon as={FaRocket} w={10} h={10} color="blue.500" />
          <Heading as="h1" size="xl" textAlign="center">
            Welcome to Science Copilot!
          </Heading>
          <Heading as="h1" size="x2" textAlign="left">
            Instructions: <br></br>
            1. Upload & Select Documents <br></br> 
            2. Ask Questions <br></br> <br></br>
            WhyHow's SDK Beta Allows Deterministic Workflows! <br></br> 
            The purpose of Science Copilot is to allow for dynamic conceptual exploration. <br></br>
            A dynamic ontology will be created based on the uploaded documents. <br></br>
            Entangle concepts between papers to draft new scientific concepts. <br></br>

          </Heading>

          <Input type="text" placeholder="Enter namespace" value={namespace} onChange={handleNamespaceChange} />

          <Input type="file" onChange={handleFileChange} />
          <Button colorScheme="blue" onClick={handleUpload} size="lg" leftIcon={<FaRocket />}>
            Upload Document
          </Button>
          <Checkbox isChecked={useRawText} onChange={() => setUseRawText(!useRawText)}>
            Use raw text for LDA
          </Checkbox>
          <Box maxH="200px" overflowY="auto" w="100%">
            <Heading as="h3" size="md">Uploaded Documents:</Heading>
            <SimpleGrid columns={2} spacing={2} mt={3}>
              {documents.map((doc, index) => (
                <Flex key={index} justify="space-between" align="center">
                  <Text>{doc}</Text>
                  <Button
                    size="sm"
                    colorScheme={isDocumentSelected(doc) ? "green" : "gray"}
                    onClick={() => toggleDocumentSelection(doc)}
                    leftIcon={<FaFileAlt />}
                  >
                    {isDocumentSelected(doc) ? "Selected" : "Select"}
                  </Button>
                  <Button
                    size="sm"
                    colorScheme="red"
                    onClick={() => handleDelete(doc)}
                    leftIcon={<FaTrash />}
                  >
                    Delete
                  </Button>
                </Flex>
              ))}
            </SimpleGrid>
          </Box>
          {importantPhrases.length > 0 && (
            <Box maxH="200px" overflowY="auto" w="100%">
              <Heading as="h3" size="md">Important Phrases:</Heading>
              <ul>
                {importantPhrases.map((topic, index) => (
                  <li key={index}>
                    {topic.map((phrase, phraseIndex) => (
                      <Badge key={phraseIndex} mr={1} colorScheme="teal">{phrase}</Badge>
                    ))}
                  </li>
                ))}
              </ul>
            </Box>
          )}
          {questions.length > 0 && (
            <Box maxH="200px" overflowY="auto" w="100%">
              <Heading as="h3" size="md">Generated Questions:</Heading>
              <ul>
                {questions.map((q, index) => (
                  <li key={index}>{q}</li>
                ))}
              </ul>
            </Box>
          )}
          <Button colorScheme="blue" onClick={handleCreateGraph} size="lg" leftIcon={<FaRocket />}>
            Create Graph
          </Button>
          <Textarea
            placeholder="Enter question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <Button colorScheme="blue" onClick={handleQuery} size="lg" leftIcon={<FaRocket />}>
            Query Graph
          </Button>
          
          <Text fontSize="lg" paddingTop={3}>Response: {message}</Text>
        </VStack>
      </Flex>
    </ChakraProvider>
  );
}
