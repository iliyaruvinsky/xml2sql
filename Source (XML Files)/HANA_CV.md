?xml version="1.0" encoding="UTF-8"?>
<Calculation:scenario xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:AccessControl="http://www.sap.com/ndb/SQLCoreModelAccessControl.ecore" xmlns:Calculation="http://www.sap.com/ndb/BiModelCalculation.ecore" schemaVersion="2.3" id="UNCLEARED_BANK_STATEMENTS" applyPrivilegeType="ANALYTIC_PRIVILEGE" checkAnalyticPrivileges="true" defaultClient="$$client$$" defaultLanguage="$$language$$" hierarchiesSQLEnabled="false" translationRelevant="true" visibility="reportingEnabled" calculationScenarioType="TREE_BASED" dataCategory="CUBE" enforceSqlExecution="false" executionSemantic="UNDEFINED" outputViewType="Aggregation">
  <origin/>
  <descriptions defaultDescription="UNCLEARED_BANK_STATEMENTS"/>
  <metadata changedAt="2025-10-23 20:10:26.869"/>
  <localVariables/>
  <variableMappings/>
  <informationModelLayout relativeWidthScenario="45"/>
  <dataSources>
    <DataSource id="FEBKO" type="DATA_BASE_TABLE">
      <viewAttributes allViewAttributes="true"/>
      <columnObject schemaName="SAPK5D" columnObjectName="FEBKO"/>
    </DataSource>
    <DataSource id="FEBEP" type="DATA_BASE_TABLE">
      <viewAttributes allViewAttributes="true"/>
      <columnObject schemaName="SAPK5D" columnObjectName="FEBEP"/>
    </DataSource>
    <DataSource id="BSEG" type="DATA_BASE_TABLE">
      <viewAttributes allViewAttributes="true"/>
      <columnObject schemaName="SAPK5D" columnObjectName="BSEG"/>
    </DataSource>
    <DataSource id="T001" type="DATA_BASE_TABLE">
      <viewAttributes allViewAttributes="true"/>
      <columnObject schemaName="SAPK5D" columnObjectName="T001"/>
    </DataSource>
  </dataSources>
  <calculationViews>
    <calculationView xsi:type="Calculation:ProjectionView" id="Projection_1">
      <descriptions/>
      <viewAttributes>
        <viewAttribute id="MANDT"/>
        <viewAttribute id="ANWND"/>
        <viewAttribute id="ABSND"/>
        <viewAttribute id="AZIDT"/>
        <viewAttribute id="EMKEY"/>
        <viewAttribute id="KUKEY"/>
        <viewAttribute id="BUKRS"/>
        <viewAttribute id="HBKID"/>
      </viewAttributes>
      <calculatedViewAttributes/>
      <input node="#FEBKO">
        <mapping xsi:type="Calculation:AttributeMapping" target="MANDT" source="MANDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="ANWND" source="ANWND"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="ABSND" source="ABSND"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="AZIDT" source="AZIDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="EMKEY" source="EMKEY"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KUKEY" source="KUKEY"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUKRS" source="BUKRS"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="HBKID" source="HBKID"/>
      </input>
    </calculationView>
    <calculationView xsi:type="Calculation:ProjectionView" id="Projection_2">
      <descriptions/>
      <viewAttributes>
        <viewAttribute id="MANDT"/>
        <viewAttribute id="KUKEY"/>
        <viewAttribute id="BELNR"/>
        <viewAttribute id="GJAHR"/>
        <viewAttribute id="BUDAT"/>
        <viewAttribute id="VALUT"/>
        <viewAttribute id="KWAER"/>
        <viewAttribute id="KWBTR"/>
        <viewAttribute id="EPVOZ"/>
      </viewAttributes>
      <calculatedViewAttributes/>
      <input node="#FEBEP">
        <mapping xsi:type="Calculation:AttributeMapping" target="MANDT" source="MANDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KUKEY" source="KUKEY"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BELNR" source="BELNR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="GJAHR" source="GJAHR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUDAT" source="BUDAT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="VALUT" source="VALUT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KWAER" source="KWAER"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KWBTR" source="KWBTR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="EPVOZ" source="EPVOZ"/>
      </input>
    </calculationView>
    <calculationView xsi:type="Calculation:JoinView" id="Join_1" joinOrder="OUTSIDE_IN" joinType="inner">
      <descriptions/>
      <viewAttributes>
        <viewAttribute id="MANDT"/>
        <viewAttribute id="KUKEY"/>
        <viewAttribute id="BUKRS"/>
        <viewAttribute id="BELNR"/>
        <viewAttribute id="GJAHR"/>
        <viewAttribute id="BUDAT"/>
        <viewAttribute id="VALUT"/>
        <viewAttribute id="KWAER"/>
        <viewAttribute id="KWBTR"/>
        <viewAttribute id="HBKID"/>
        <viewAttribute id="EPVOZ"/>
      </viewAttributes>
      <calculatedViewAttributes/>
      <input node="#Projection_1">
        <mapping xsi:type="Calculation:AttributeMapping" target="MANDT" source="MANDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KUKEY" source="KUKEY"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUKRS" source="BUKRS"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="HBKID" source="HBKID"/>
      </input>
      <input node="#Projection_2">
        <mapping xsi:type="Calculation:AttributeMapping" target="BELNR" source="BELNR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="GJAHR" source="GJAHR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUDAT" source="BUDAT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="VALUT" source="VALUT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KWAER" source="KWAER"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KWBTR" source="KWBTR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="EPVOZ" source="EPVOZ"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="MANDT" source="MANDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KUKEY" source="KUKEY"/>
      </input>
      <joinAttribute name="MANDT"/>
      <joinAttribute name="KUKEY"/>
    </calculationView>
    <calculationView xsi:type="Calculation:ProjectionView" id="Projection_3">
      <descriptions/>
      <viewAttributes>
        <viewAttribute id="MANDT"/>
        <viewAttribute id="BUKRS"/>
        <viewAttribute id="BELNR"/>
        <viewAttribute id="GJAHR"/>
        <viewAttribute id="AUGBL">
          <filter xsi:type="AccessControl:SingleValueFilter" including="true" value=""/>
        </viewAttribute>
        <viewAttribute id="BUZEI"/>
        <viewAttribute id="AUGDT"/>
        <viewAttribute id="KOART"/>
        <viewAttribute id="SHKZG"/>
        <viewAttribute id="DMBTR"/>
        <viewAttribute id="WRBTR"/>
        <viewAttribute id="XOPVW">
          <filter xsi:type="AccessControl:SingleValueFilter" including="true" value="X"/>
        </viewAttribute>
      </viewAttributes>
      <calculatedViewAttributes/>
      <input node="#BSEG">
        <mapping xsi:type="Calculation:AttributeMapping" target="MANDT" source="MANDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUKRS" source="BUKRS"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BELNR" source="BELNR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="GJAHR" source="GJAHR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="AUGBL" source="AUGBL"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUZEI" source="BUZEI"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="AUGDT" source="AUGDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KOART" source="KOART"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="SHKZG" source="SHKZG"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="DMBTR" source="DMBTR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="WRBTR" source="WRBTR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="XOPVW" source="XOPVW"/>
      </input>
    </calculationView>
    <calculationView xsi:type="Calculation:JoinView" id="Join_2" joinOrder="OUTSIDE_IN" joinType="inner">
      <descriptions/>
      <viewAttributes>
        <viewAttribute id="MANDT"/>
        <viewAttribute id="KUKEY"/>
        <viewAttribute id="BUKRS"/>
        <viewAttribute id="BELNR"/>
        <viewAttribute id="GJAHR"/>
        <viewAttribute id="BUDAT"/>
        <viewAttribute id="VALUT"/>
        <viewAttribute id="KWAER"/>
        <viewAttribute id="KWBTR"/>
        <viewAttribute id="HBKID"/>
        <viewAttribute id="EPVOZ"/>
      </viewAttributes>
      <calculatedViewAttributes>
        <calculatedViewAttribute datatype="DECIMAL" id="Calc_KWBTR" length="13" scale="2" expressionLanguage="COLUMN_ENGINE">
          <formula>if(&quot;EPVOZ&quot;='S',-&quot;KWBTR&quot;,&quot;KWBTR&quot;)</formula>
        </calculatedViewAttribute>
      </calculatedViewAttributes>
      <input node="#Join_1">
        <mapping xsi:type="Calculation:AttributeMapping" target="MANDT" source="MANDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KUKEY" source="KUKEY"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUKRS" source="BUKRS"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BELNR" source="BELNR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="GJAHR" source="GJAHR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUDAT" source="BUDAT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="VALUT" source="VALUT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KWAER" source="KWAER"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KWBTR" source="KWBTR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="HBKID" source="HBKID"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="EPVOZ" source="EPVOZ"/>
      </input>
      <input node="#Projection_3">
        <mapping xsi:type="Calculation:AttributeMapping" target="MANDT" source="MANDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUKRS" source="BUKRS"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BELNR" source="BELNR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="GJAHR" source="GJAHR"/>
      </input>
      <joinAttribute name="MANDT"/>
      <joinAttribute name="BUKRS"/>
      <joinAttribute name="BELNR"/>
      <joinAttribute name="GJAHR"/>
    </calculationView>
    <calculationView xsi:type="Calculation:ProjectionView" id="Projection_4">
      <descriptions/>
      <viewAttributes>
        <viewAttribute id="MANDT"/>
        <viewAttribute id="BUKRS"/>
        <viewAttribute id="LC"/>
      </viewAttributes>
      <calculatedViewAttributes/>
      <input node="#T001">
        <mapping xsi:type="Calculation:AttributeMapping" target="MANDT" source="MANDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUKRS" source="BUKRS"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="LC" source="WAERS"/>
      </input>
    </calculationView>
    <calculationView xsi:type="Calculation:JoinView" id="Join_3" joinOrder="OUTSIDE_IN" joinType="inner">
      <descriptions/>
      <viewAttributes>
        <viewAttribute id="MANDT"/>
        <viewAttribute id="KUKEY"/>
        <viewAttribute id="BUKRS"/>
        <viewAttribute id="BELNR"/>
        <viewAttribute id="GJAHR"/>
        <viewAttribute id="BUDAT"/>
        <viewAttribute id="VALUT"/>
        <viewAttribute id="KWAER"/>
        <viewAttribute id="KWBTR"/>
        <viewAttribute id="LC"/>
        <viewAttribute id="HBKID"/>
        <viewAttribute id="Calc_KWBTR"/>
      </viewAttributes>
      <calculatedViewAttributes/>
      <input node="#Join_2">
        <mapping xsi:type="Calculation:AttributeMapping" target="MANDT" source="MANDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KUKEY" source="KUKEY"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUKRS" source="BUKRS"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BELNR" source="BELNR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="GJAHR" source="GJAHR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUDAT" source="BUDAT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="VALUT" source="VALUT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KWAER" source="KWAER"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="KWBTR" source="KWBTR"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="HBKID" source="HBKID"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="Calc_KWBTR" source="Calc_KWBTR"/>
      </input>
      <input node="#Projection_4">
        <mapping xsi:type="Calculation:AttributeMapping" target="LC" source="LC"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="MANDT" source="MANDT"/>
        <mapping xsi:type="Calculation:AttributeMapping" target="BUKRS" source="BUKRS"/>
      </input>
      <joinAttribute name="MANDT"/>
      <joinAttribute name="BUKRS"/>
    </calculationView>
  </calculationViews>
  <logicalModel id="Join_3">
    <descriptions/>
    <attributes>
      <attribute id="MANDT" order="1" attributeHierarchyActive="false" displayAttribute="false">
        <descriptions defaultDescription="MANDT"/>
        <keyMapping columnObjectName="Join_3" columnName="MANDT"/>
      </attribute>
      <attribute id="KUKEY" order="2" attributeHierarchyActive="false" displayAttribute="false">
        <descriptions defaultDescription="KUKEY"/>
        <keyMapping columnObjectName="Join_3" columnName="KUKEY"/>
      </attribute>
      <attribute id="BUKRS" order="3" attributeHierarchyActive="false" displayAttribute="false">
        <descriptions defaultDescription="BUKRS"/>
        <keyMapping columnObjectName="Join_3" columnName="BUKRS"/>
      </attribute>
      <attribute id="BELNR" order="4" attributeHierarchyActive="false" displayAttribute="false">
        <descriptions defaultDescription="BELNR"/>
        <keyMapping columnObjectName="Join_3" columnName="BELNR"/>
      </attribute>
      <attribute id="GJAHR" order="5" attributeHierarchyActive="false" displayAttribute="false">
        <descriptions defaultDescription="GJAHR"/>
        <keyMapping columnObjectName="Join_3" columnName="GJAHR"/>
      </attribute>
      <attribute id="BUDAT" order="6" attributeHierarchyActive="false" displayAttribute="false">
        <descriptions defaultDescription="BUDAT"/>
        <keyMapping columnObjectName="Join_3" columnName="BUDAT"/>
      </attribute>
      <attribute id="VALUT" order="7" attributeHierarchyActive="false" displayAttribute="false">
        <descriptions defaultDescription="VALUT"/>
        <keyMapping columnObjectName="Join_3" columnName="VALUT"/>
      </attribute>
      <attribute id="KWAER" order="8" attributeHierarchyActive="false" displayAttribute="false">
        <descriptions defaultDescription="KWAER"/>
        <keyMapping columnObjectName="Join_3" columnName="KWAER"/>
      </attribute>
      <attribute id="LC" order="9" attributeHierarchyActive="false" displayAttribute="false">
        <descriptions defaultDescription="LC"/>
        <keyMapping columnObjectName="Join_3" columnName="LC"/>
      </attribute>
      <attribute id="HBKID" order="10" semanticType="empty" attributeHierarchyActive="false" displayAttribute="false">
        <descriptions/>
        <keyMapping columnObjectName="Join_3" columnName="HBKID"/>
      </attribute>
    </attributes>
    <calculatedAttributes/>
    <privateDataFoundation>
      <tableProxies/>
      <joins/>
      <layout>
        <shapes/>
      </layout>
    </privateDataFoundation>
    <baseMeasures>
      <measure id="Calc_KWBTR" order="14" aggregationType="sum" measureType="simple">
        <descriptions defaultDescription="Calc_KWBTR"/>
        <measureMapping columnObjectName="Join_3" columnName="Calc_KWBTR"/>
      </measure>
    </baseMeasures>
    <calculatedMeasures>
      <measure id="DMBTR" hidden="false" order="11" semanticType="amount" aggregationType="sum" measureType="amount" datatype="DECIMAL" expressionLanguage="COLUMN_ENGINE" length="13" scale="2">
        <descriptions defaultDescription="DMBTR"/>
        <unitCurrencyAttribute attributeName="LC"/>
        <currencyConversion errorHandling="setToNull" generateOutputUnitCurrencyAttribute="false" outputUnitCurrencyAttributeName="">
          <client>
            <attribute attributeName="MANDT"/>
          </client>
          <schema schemaName="ABAP"/>
          <sourceCurrency>
            <attribute attributeName="KWAER"/>
          </sourceCurrency>
          <erpDecimalShift>true</erpDecimalShift>
          <erpDecimalShiftBack>false</erpDecimalShiftBack>
          <targetCurrency>
            <attribute attributeName="LC"/>
          </targetCurrency>
          <referenceDate>
            <attribute attributeName="VALUT"/>
          </referenceDate>
          <exchangeRateType>M</exchangeRateType>
        </currencyConversion>
        <formula>&quot;Calc_KWBTR&quot;</formula>
      </measure>
      <measure id="DMBE2" hidden="false" order="12" semanticType="amount" aggregationType="sum" measureType="amount" datatype="DECIMAL" expressionLanguage="COLUMN_ENGINE" length="13" scale="2">
        <descriptions defaultDescription="DMBE2"/>
        <fixedCurrency>EUR</fixedCurrency>
        <currencyConversion errorHandling="setToNull" generateOutputUnitCurrencyAttribute="false" outputUnitCurrencyAttributeName="">
          <client>
            <attribute attributeName="MANDT"/>
          </client>
          <schema schemaName="ABAP"/>
          <sourceCurrency>
            <attribute attributeName="KWAER"/>
          </sourceCurrency>
          <erpDecimalShift>true</erpDecimalShift>
          <erpDecimalShiftBack>false</erpDecimalShiftBack>
          <targetCurrency>
            <value>EUR</value>
          </targetCurrency>
          <referenceDate>
            <attribute attributeName="VALUT"/>
          </referenceDate>
          <exchangeRateType>M</exchangeRateType>
        </currencyConversion>
        <formula>&quot;Calc_KWBTR&quot;</formula>
      </measure>
      <measure id="DMBE3" hidden="false" order="13" semanticType="amount" aggregationType="sum" measureType="amount" datatype="DECIMAL" expressionLanguage="COLUMN_ENGINE" length="13" scale="2">
        <descriptions defaultDescription="DMBE3"/>
        <fixedCurrency>USD</fixedCurrency>
        <currencyConversion errorHandling="setToNull" generateOutputUnitCurrencyAttribute="false" outputUnitCurrencyAttributeName="">
          <client>
            <attribute attributeName="MANDT"/>
          </client>
          <schema schemaName="ABAP"/>
          <sourceCurrency>
            <attribute attributeName="KWAER"/>
          </sourceCurrency>
          <erpDecimalShift>true</erpDecimalShift>
          <erpDecimalShiftBack>false</erpDecimalShiftBack>
          <targetCurrency>
            <value>USD</value>
          </targetCurrency>
          <referenceDate>
            <attribute attributeName="VALUT"/>
          </referenceDate>
          <exchangeRateType>M</exchangeRateType>
        </currencyConversion>
        <formula>&quot;Calc_KWBTR&quot;</formula>
      </measure>
    </calculatedMeasures>
    <restrictedMeasures/>
    <localDimensions/>
  </logicalModel>
  <layout>
    <shapes>
      <shape expanded="true" modelObjectName="Output" modelObjectNameSpace="MeasureGroup">
        <upperLeftCorner x="99" y="87"/>
        <rectangleSize/>
      </shape>
      <shape expanded="true" modelObjectName="Projection_1" modelObjectNameSpace="CalculationView">
        <upperLeftCorner x="22" y="453"/>
        <rectangleSize height="-1" width="-1"/>
      </shape>
      <shape expanded="true" modelObjectName="Projection_2" modelObjectNameSpace="CalculationView">
        <upperLeftCorner x="176" y="453"/>
        <rectangleSize height="-1" width="-1"/>
      </shape>
      <shape expanded="true" modelObjectName="Join_1" modelObjectNameSpace="CalculationView">
        <upperLeftCorner x="99" y="357"/>
        <rectangleSize height="-1" width="-1"/>
      </shape>
      <shape expanded="true" modelObjectName="Projection_3" modelObjectNameSpace="CalculationView">
        <upperLeftCorner x="253" y="357"/>
        <rectangleSize height="-1" width="-1"/>
      </shape>
      <shape expanded="true" modelObjectName="Join_2" modelObjectNameSpace="CalculationView">
        <upperLeftCorner x="176" y="261"/>
        <rectangleSize height="-1" width="-1"/>
      </shape>
      <shape expanded="true" modelObjectName="Projection_4" modelObjectNameSpace="CalculationView">
        <upperLeftCorner x="22" y="261"/>
        <rectangleSize height="-1" width="-1"/>
      </shape>
      <shape expanded="true" modelObjectName="Join_3" modelObjectNameSpace="CalculationView">
        <upperLeftCorner x="99" y="165"/>
        <rectangleSize height="-1" width="-1"/>
      </shape>
    </shapes>
  </layout>
</Calculation:scenario>